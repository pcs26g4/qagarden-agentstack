import asyncio
import json
import os
import logging
import urllib.request
from datetime import datetime
from typing import Dict, Any, Optional

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

import sys
from pathlib import Path

# Dynamically add agent subdirectories to search path
CURRENT_DIR = Path(__file__).parent.resolve()
CRAWLER_DIR = CURRENT_DIR / "crawler"

if str(CRAWLER_DIR) not in sys.path:
    sys.path.append(str(CRAWLER_DIR))

try:
    from qa_garden_crawler import QAGardenCrawler
    from config import CrawlerConfig
    from synthesis import DataSynthesizer
except ImportError:
    try:
        from crawler.qa_garden_crawler import QAGardenCrawler
        from crawler.config import CrawlerConfig
        from crawler.synthesis import DataSynthesizer
    except ImportError as e:
        logger.error(f"Failed to import Crawler components: {e}")


class PipelineOrchestrator:
    """
    End-to-end Orchestrator for the QA Garden Pipeline.
    Connects all 5 agents: Crawler -> Synthesis -> PlaywrightGen -> Executor -> Triage
    Works for any given website URL - no hardcoded config.
    """

    def __init__(self, status_file: Optional[str] = None):
        if status_file is None:
            # v9.0: Move status file to /tmp on Linux to prevent PM2 watch restarts in cwd
            if os.name != "nt":
                status_file = "/tmp/pipeline_status.json"
            else:
                status_file = str(CURRENT_DIR / "pipeline_status.json")
        logger.info(f"Initializing Orchestrator with status file: {status_file}")
        self.status_file = status_file
        self.current_job_id: Optional[str] = None
        self.aborted: bool = False
        self.raw_locators_path: Optional[str] = None
        self.synthesized_path: Optional[str] = None
        self.broadcast_queues: Dict[str, asyncio.Queue] = {} # Map job_id to its UI queue
        self.status: Dict[str, Any] = {
            "job_id": None,
            "status": "idle",
            "current_stage": None,
            "stages": {
                "crawler":       {"status": "pending", "progress": 0, "error": None},
                "synthesis":     {"status": "pending", "progress": 0, "error": None},
                "playwright_gen":{"status": "pending", "progress": 0, "error": None},
                "triage":        {"status": "pending", "progress": 0, "error": None},
            },
            "start_time": None,
            "end_time":   None,
            "last_run":   None,
            "error":      None,
        }
        self.pause_event = asyncio.Event()
        self.pause_event.set() # Unpaused by default
        self._load_status()

    # -------------------------------------------------------------------------
    # Status persistence
    # -------------------------------------------------------------------------
    def _load_status(self):
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, "r") as f:
                    old = json.load(f)
                    self.status["last_run"] = old.get("last_run")
            except Exception:
                pass

    def _save_status(self):
        try:
            with open(self.status_file, "w") as f:
                json.dump(self.status, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    async def update_stage(self, stage: str, status: str, progress: int = 0, error: Optional[str] = None, metrics: Dict = None):
        stages = self.status.setdefault("stages", {})
        if stage not in stages:
            stages[stage] = {"status": "idle", "progress": 0, "error": None}
        
        stages[stage]["status"]   = status
        stages[stage]["progress"] = progress
        stages[stage]["error"]    = error
        
        if metrics:
            for k, v in metrics.items():
                stages[stage][k] = v

        self.status["current_stage"] = stage
        self._save_status()

        # Broadcast to UI if a queue exists for this job
        if self.current_job_id and self.current_job_id in self.broadcast_queues:
            try:
                # v7.6: Flatten metrics at the root for UI 'use-websocket' compatibility
                update_msg = {
                    "event": "progress",
                    "agent": stage,
                    "status": status,
                    "progress": progress,
                    "error": error,
                    "elements": stages[stage].get("elements", stages[stage].get("locators", 0)),
                    "discovered": stages[stage].get("discovered", stages[stage].get("pages", 0)),
                    "finished": stages[stage].get("finished", 0),
                    "duration": stages[stage].get("duration", 0),
                    "metrics": stages[stage] # Keep full dict for detail view
                }
                self.broadcast_queues[self.current_job_id].put_nowait(update_msg)
            except Exception as e:
                logger.debug(f"Broadcast failed: {e}")

    # -------------------------------------------------------------------------
    # Control API
    # -------------------------------------------------------------------------
    def pause(self):
        logger.info(f"Pipeline {self.current_job_id} PAUSED")
        self.pause_event.clear()
        self.status["status"] = "paused"
        self._save_status()

    def resume(self):
        logger.info(f"Pipeline {self.current_job_id} RESUMED")
        self.pause_event.set()
        self.status["status"] = "running"
        self._save_status()

    def abort(self):
        logger.info(f"Pipeline {self.current_job_id} ABORTED")
        self.aborted = True
        self.pause_event.set() # Ensure we wake up from pause to exit
        self.status["status"] = "failed"
        self.status["error"] = "Aborted by user"
        self._save_status()

    def _pre_pipeline_reset(self):
        """Phase 19: Deep Reset of all agent workspaces to prevent cross-run pollution."""
        import shutil
        logger.info("[Orchestrator] Performing Pre-Pipeline Deep Reset...")
        
        folders_to_clear = [
            CURRENT_DIR / "playwright_gen" / "config",
            CURRENT_DIR / "playwright_gen" / "testcases",
            CURRENT_DIR / "playwright_gen" / "tests",
            CURRENT_DIR / "cicd" / "config",
            CURRENT_DIR / "cicd" / "testcases",
            CURRENT_DIR / "cicd" / "tests",
        ]
        
        for ddir in folders_to_clear:
            if ddir.exists():
                try:
                    # v25.0: More robust cleanup for Windows/Linux
                    import stat
                    for item in ddir.iterdir():
                        try:
                            if item.is_file() or item.is_symlink():
                                item.chmod(stat.S_IWRITE)
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                        except Exception as e:
                            logger.warning(f"  [Reset] Could not delete {item}: {e}")
                    logger.debug(f"  [Reset] Cleared: {ddir}")
                except Exception as e:
                    logger.warning(f"  [Reset] Failed to clear {ddir}: {e}")
            ddir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Main entry point
    # -------------------------------------------------------------------------
    async def run_pipeline(self, target_url: str, credentials: Dict[str, str], job_id: str, broadcast_queue: Optional[asyncio.Queue] = None, max_depth: int = 3, max_pages: int = 30):
        """Run the complete QA pipeline for any website URL."""
        # Phase 19: Clear stale directories BEFORE starting any stage
        # This ensures Stage 2 handover files aren't wiped by Stage 3
        self._pre_pipeline_reset()

        self.current_job_id = job_id
        self.aborted = False
        
        if broadcast_queue:
            self.broadcast_queues[job_id] = broadcast_queue

        self.status.update({
            "job_id":     job_id,
            "status":     "running",
            "start_time": datetime.now().isoformat(),
            "error":      None,
        })
        # Reset all stage statuses
        for s in self.status["stages"].values():
            s.update({"status": "pending", "progress": 0, "error": None})
        self._save_status()

        try:
            if not target_url.startswith("http"):
                raise ValueError(f"Invalid Target URL: {target_url}")

            # Stage 1 - Crawler
            await self._execute_stage("crawler",        self._run_crawler, target_url, credentials, max_depth, max_pages)
            # Stage 2 - Synthesis + auto-generate urls.py
            await self._execute_stage("synthesis",      self._run_synthesis, target_url)
            # Stage 3 - Playwright script generation
            await self._execute_stage("playwright_gen", self._run_playwright_gen)
            # Stage 4 - Wait for CI/CD Execution
            await self._execute_stage("cicd",   self._wait_for_cicd)
            # Stage 5 - Failure Triage (only if needed)
            await self._execute_stage("triage", self._run_triage)

            self.status.update({
                "status":   "completed",
                "end_time": datetime.now().isoformat(),
                "last_run": datetime.now().isoformat(),
            })
            logger.info("Pipeline completed successfully.")
            # Broadcast final completion to WebSocket so UI turns green
            if job_id in self.broadcast_queues:
                self.broadcast_queues[job_id].put_nowait({
                    "event": "completed",
                    "agent": "pipeline",
                    "status": "completed",
                    "progress": 100,
                    "message": "Pipeline completed successfully.",
                    "stages": self.status.get("stages", {}),
                })

        except Exception as e:
            logger.error(f"Pipeline failed at {self.status.get('current_stage')}: {e}")
            self.status.update({
                "status":   "failed",
                "error":    str(e),
                "last_run": datetime.now().isoformat(),
            })
            # Broadcast failure to WebSocket so UI shows failed state
            if job_id in self.broadcast_queues:
                self.broadcast_queues[job_id].put_nowait({
                    "event": "completed",
                    "agent": "pipeline",
                    "status": "failed",
                    "progress": 0,
                    "message": f"Pipeline failed: {e}",
                    "stages": self.status.get("stages", {}),
                })
        finally:
            self._save_status()
            await asyncio.sleep(10)
            if self.status["status"] != "running":
                self.status.update({"status": "idle", "current_stage": None})
                self._save_status()

    async def _execute_stage(self, stage_name: str, func, *args):
        if self.aborted:
            raise InterruptedError("Pipeline aborted by user.")
        
        # Respect pause before starting stage
        await self.pause_event.wait()
        
        await self.update_stage(stage_name, "running", 10)
        try:
            # We wrap the stage function to periodically check for pause/abort
            await asyncio.wait_for(func(*args), timeout=1800.0)   # 30-min per stage
            await self.update_stage(stage_name, "completed", 100)
            
            # Broadcast stage completion to WebSocket - use BOTH 'stage_complete' and 'completed' for UI compatibility
            job_id = self.current_job_id
            if job_id and job_id in self.broadcast_queues:
                st_data = self.status.get("stages", {}).get(stage_name, {})
                completed_payload = {
                    "event": "completed", # Frontend listens specifically for 'completed' to trigger port-switch handovers
                    "agent": stage_name,
                    "status": "completed",
                    "progress": 100,
                    "message": f"Stage {stage_name} completed.",
                    "elements": st_data.get("elements", st_data.get("locators", 0)),
                    "discovered": st_data.get("discovered", st_data.get("pages", 0)),
                    "finished": st_data.get("finished", 0),
                    "duration": st_data.get("duration", 0),
                    "metrics": st_data  # Keep full dict for detail view
                }
                self.broadcast_queues[job_id].put_nowait(completed_payload)
                
                # Backwards compatibility event
                self.broadcast_queues[job_id].put_nowait({
                    **completed_payload,
                    "event": "stage_complete"
                })
        except asyncio.TimeoutError:
            await self.update_stage(stage_name, "failed", error="Stage timed out (30 min)")
            raise TimeoutError(f"Stage {stage_name} timed out.")
        except Exception as e:
            await self.update_stage(stage_name, "failed", error=str(e))
            raise

    # -------------------------------------------------------------------------
    # Stage 1 - Crawler
    # -------------------------------------------------------------------------
    async def _run_crawler(self, url: str, creds: Dict, max_depth: int = 3, max_pages: int = 50):
        logger.info(f"[Stage 1] Crawling {url} (Depth: {max_depth}, Pages: {max_pages}) ...")
        config = CrawlerConfig(
            url=url, 
            auth_creds=creds, 
            max_depth=max_depth, 
            max_pages=max_pages, 
            use_ai=True,
            headless=True # Ensure headless on EC2
        )
        crawler = QAGardenCrawler(config)
        
        # Link orchestrator control events to crawler
        crawler.pause_event = self.pause_event

        pages_indexed = 0
        async for update in crawler.run():
            if update.get("event") == "progress":
                metrics = update.get("metrics", {})
                pages_indexed = metrics.get("finished", 0)
                elements = metrics.get("elements", 0)
                discovered = metrics.get("discovered", 0)
                cov = metrics.get("coverage", 0)
                
                # Update orchestrator status with metrics (flattened broadcast happens inside)
                await self.update_stage("crawler", "running", progress=int(cov), metrics={
                    "elements": elements,
                    "discovered": discovered,
                    "finished": pages_indexed,
                    "coverage": cov,
                    "url": update.get("url", "")
                })
            if self.aborted:
                raise InterruptedError("Aborted during crawl.")

        # Stage Guardrail: Verify that we actually crawled something
        self.raw_locators_path = str(crawler.locators_dir) if hasattr(crawler, "locators_dir") else None

        # Check for page_*.json files (the actual output format)
        page_files = []
        if self.raw_locators_path and os.path.isdir(self.raw_locators_path):
            page_files = [f for f in os.listdir(self.raw_locators_path) if f.startswith("page_") and f.endswith(".json")]

        if not page_files:
            logger.error(f"[Stage 1] FAIL: No page_*.json locators generated in {self.raw_locators_path}")
            raise RuntimeError("Crawler failed to index target site. Check URL or firewall settings.")
            
        # v19.2: Real disk-based count for the summary report
        real_pages = len(page_files)
        total_locators = len(crawler.all_locators)
        logger.info(f"[Stage 1] Done. {real_pages} pages indexed. {total_locators} total locators. Locators -> {self.raw_locators_path}")
        
        # Ensure final metrics are sent to UI
        await self.update_stage("crawler", "completed", progress=100, metrics={
            "elements": total_locators,
            "finished": real_pages,
            "discovered": len(crawler.discovered_urls),
            "coverage": 100
        })

    # -------------------------------------------------------------------------
    # Stage 2 - Synthesis + auto-generate urls.py
    # -------------------------------------------------------------------------
    async def _run_synthesis(self, target_url: str):
        logger.info("[Stage 2] Synthesis ...")

        if not self.raw_locators_path or not os.path.isdir(self.raw_locators_path):
            logger.error(f"[Stage 2] FAIL: Invalid raw locators path: {self.raw_locators_path}")
            raise RuntimeError("Synthesis failed: No input data from Crawler.")

        try:
            # v7.8: Job-specific consolidated path for multi-website support
            job_id = self.current_job_id
            cons_dir = CURRENT_DIR / f"locators_consolidated_{job_id}"
            cons_dir.mkdir(parents=True, exist_ok=True)
            
            from crawler.synthesis import DataSynthesizer
            syn = DataSynthesizer(output_dir=str(cons_dir))
            syn_result = syn.synthesize_directory(self.raw_locators_path)
            self.synthesized_path = syn_result["path"]
            
            # v23.1: Update synthesis stage with real metrics from DataSynthesizer
            await self.update_stage("synthesis", "completed", progress=100, metrics={
                "elements": syn_result["total_locators"],
                "finished": syn_result["total_pages"],
                "discovered": syn_result["raw_locators"]
            })

            # v7.5: Ensure individual page_*.json files are copied to the consolidated folder
            # so the Test Generator (8001) can find them during handover.
            if self.synthesized_path:
                import shutil
                dest_dir = Path(self.synthesized_path).parent
                src_dir = Path(self.raw_locators_path)
                for jf in src_dir.glob("page_*.json"):
                    shutil.copy2(jf, dest_dir / jf.name)
                logger.info(f"[Stage 2] Copied page files to {dest_dir} for Test Case Gen.")

            if not self.synthesized_path or not os.path.exists(self.synthesized_path):
                logger.warning(f"DataSynthesizer produced no output. Falling back to raw locators.")
                self.synthesized_path = self.raw_locators_path
        except Exception as e:
            logger.warning(f"DataSynthesizer failed (non-fatal): {e}")
            self.synthesized_path = self.raw_locators_path

        # Copy locator JSONs into playwright_gen/config/ and cicd/config/
        # so generate_script.py can discover and read them
        await self._copy_locators_to_agents()

        await self._auto_generate_urls_py(target_url)
        logger.info("[Stage 2] Done.")

    async def _copy_locators_to_agents(self):
        """
        Copy page_*.json locator files from the crawler's output directory
        into agents/playwright_gen/config/ and agents/cicd/config/.

        This is the critical bridge that makes generate_script.py work -
        without these files being present in playwright_gen/config/, the
        script generator has no locators to process and produces no output.
        """
        import shutil

        # Determine source: prefer synthesized path, fall back to raw locators
        src_dir_str = self.synthesized_path or self.raw_locators_path

        # Fallback scan if orchestrator path is not set
        candidates = [
            Path(src_dir_str) if src_dir_str else None,
            CURRENT_DIR / "crawler" / "locators_new",
            CURRENT_DIR / "locators_new",
        ]
        src_dir = next((c for c in candidates if c and c.is_dir()), None)

        if not src_dir:
            logger.warning("[Stage 2] _copy_locators_to_agents: no locator directory found, skipping copy.")
            return

        json_files = list(src_dir.rglob("page_*.json"))
        if not json_files:
            logger.warning(f"[Stage 2] No page_*.json files in {src_dir}. Check crawler output.")
            return

        logger.info(f"[Stage 2] Copying {len(json_files)} locator JSON files from {src_dir}")

        for agent in ("playwright_gen", "cicd"):
            cfg_dir = CURRENT_DIR / agent / "config"
            cfg_dir.mkdir(parents=True, exist_ok=True)
            copied = 0
            for jf in json_files:
                # Rename page_N.json to page_N_locators.json for Test Generator / Architect compatibility
                new_name = jf.name.replace(".json", "_locators.json") if jf.name.startswith("page_") else jf.name
                dest = cfg_dir / new_name
                try:
                    shutil.copy2(jf, dest)
                    copied += 1
                except Exception as e:
                    logger.warning(f"  Could not copy {jf.name} -> {agent}/config/{new_name}: {e}")
            logger.info(f"  -> Copied {copied}/{len(json_files)} locator files to {agent}/config/ (renamed to *_locators.json)")
            
            # v7.2: Also copy consolidated_locators.json if available
            consolidated_file = src_dir / "consolidated_locators.json"
            if not consolidated_file.exists():
                # Fallback to parent dir (locators_root)
                consolidated_file = src_dir.parent / "consolidated_locators.json"
            
            if consolidated_file.exists():
                dest_cons = cfg_dir / "consolidated_locators.json"
                try:
                    shutil.copy2(consolidated_file, dest_cons)
                    logger.info(f"  -> Copied consolidated_locators.json to {agent}/config/")
                except Exception as e:
                    logger.warning(f"  Could not copy consolidated_locators.json: {e}")


    async def _auto_generate_urls_py(self, target_url: str):
        """
        Scans the locators directory for page_*.json files, extracts their URLs,
        and writes a fresh urls.py into both playwright_gen/config/ and cicd/config/.
        This is what makes the pipeline work for ANY website - no manual config needed.
        """
        logger.info("Auto-generating urls.py ...")

        # Find the locators folder
        candidates = [
            Path(self.raw_locators_path) if self.raw_locators_path else None,
            CURRENT_DIR / "playwright_gen" / "locators_new",
            CURRENT_DIR / "locators_new",
            CURRENT_DIR / "crawler" / "locators_new",
        ]
        loc_dir = next((c for c in candidates if c and c.is_dir()), None)
        logger.info(f"Scanning for locators in: {loc_dir}")

        page_entries: Dict[str, str] = {}
        if loc_dir:
            json_files = list(loc_dir.rglob("page_*.json"))
            logger.info(f"Found {len(json_files)} page_*.json files in {loc_dir}")
            for jf in sorted(json_files):
                page_id = jf.stem
                try:
                    with open(jf, encoding="utf-8") as f:
                        data = json.load(f)
                    page_url = data.get("url") or data.get("page_url") or target_url
                    page_entries[page_id] = page_url
                except Exception:
                    page_entries[page_id] = target_url

        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        base   = f"{parsed.scheme}://{parsed.netloc}/"

        lines = [
            "# Auto-generated by QA Garden Orchestrator - do not edit manually",
            f'BASE_URL = "{base}"',
            "",
        ]
        for page_id, url in page_entries.items():
            lines.append(f'{page_id.upper()}_URL = "{url}"')
        lines += [
            "",
            f'LOGIN_URL   = "{target_url}"',
            f'SIGNUP_URL  = "{target_url}"',
            f'WELCOME_URL = "{target_url}"',
        ]
        content = "\n".join(lines) + "\n"

        for agent in ("playwright_gen", "cicd"):
            cfg_dir = CURRENT_DIR / agent / "config"
            cfg_dir.mkdir(parents=True, exist_ok=True)
            (cfg_dir / "urls.py").write_text(content, encoding="utf-8")
            logger.info(f"  -> wrote {agent}/config/urls.py  ({len(page_entries)} pages)")

        # Trigger Test Case Generation (Agent on port 8001)
        await self._run_test_case_gen(target_url)

    async def _run_test_case_gen(self, target_url: str):
        # Stage 2.5: Generate test cases from locators.
        # Calls the Test Generator agent on port 8001.
        #
        # IMPORTANT: We pass the raw crawler output path, NOT the playwright_gen/config path,
        # because 8001 WIPES the playwright_gen directories at the start of its bridge logic.
        """
        Stage 2.5: Generate test cases from locators.
        """
        import urllib.request, urllib.error
        tg_url = os.getenv("TEST_GENERATOR_URL", "http://localhost:8001")
        job_id = self.current_job_id
        
        logger.info(f"[Stage 2.5] Triggering Test Case Gen at {tg_url} ...")
        
        # Use the raw locators from Stage 1 or the synthesized ones
        locators_path = self.synthesized_path or self.raw_locators_path
        if not locators_path:
            logger.warning("[Stage 2.5] No locators path found. Skipping.")
            return

        try:
            body = json.dumps({
                "run_id": job_id,
                "locators_path": str(locators_path),
                "target_url": target_url
            }).encode()
            req = urllib.request.Request(
                f"{tg_url}/api/v1/generate-tests", data=body,
                headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
                logger.info(f"Test Case Gen API response: {result}")
        except Exception as e:
            logger.warning(f"[Stage 2.5] Failed to trigger Test Generator (8001): {e}")
            return # Non-fatal, Stage 3 might have fallbacks or existing files

        # Poll for completion (8001 is async)
        # It uses SSE but also has /job status usually or we can check its output
        # For now, we'll wait a bit or if there's no status endpoint, we'll assume it's running
        # Actually, 8001 usually takes 30-60s. 
        # Let's check for a job status endpoint on 8001. 
        # Looking at 8001 code... it doesn't have /job/{id} in the root, maybe in the router?
        # Re-checking 8001 main.py... it only has /ws/{id} and SSE.
        # However, the bridge in 8001 calls 8002. So maybe 8001 is the trigger for 8002?
        # In orchestrator, we want to stay in control.
        # We'll sleep for 45 seconds as a rough estimate if we can't poll.
        # Poll for completion (8001 is async)
        # v7.2: Dynamic Polling instead of 45s hardcoded sleep
        logger.info(f"[Stage 2.5] Polling status at {tg_url}/api/v1/job/{job_id} ...")
        for i in range(150): # 5 mins max
            if self.aborted:
                raise InterruptedError()
            await asyncio.sleep(2)
            try:
                with urllib.request.urlopen(f"{tg_url}/api/v1/job/{job_id}", timeout=5) as r:
                    d = json.loads(r.read())
                    st = d.get("status")
                    count = d.get("testCaseCount", d.get("test_case_count", 0))
                    prog = d.get("progress", 10 + min(i * 2, 80))
                    
                    metrics_data = d.get("metrics", {})
                    valid_locs = metrics_data.get("valid_locators", count)
                    components = metrics_data.get("components", 1)
                    
                    # Update metrics during polling so Home page stays alive
                    await self.update_stage("synthesis", "running", progress=prog, metrics={
                        "elements": valid_locs,
                        "finished": components,
                        "valid_locators": valid_locs,
                        "components": components,
                        "test_cases": count
                    })

                    if st == "completed":
                        logger.info(f"[Stage 2.5] Done. {count} test cases generated.")
                        # Update synthesis stage with final metrics
                        await self.update_stage("synthesis", "completed", progress=100, metrics={
                            "elements": valid_locs,
                            "finished": components,
                            "valid_locators": valid_locs,
                            "components": components,
                            "test_cases": count
                        })
                        return
                    if st == "failed":
                        raise RuntimeError(f"Test Generator failed: {d.get('message') or 'Unknown error'}")
                    # Update progress in Orchestrator status so UI shows movement
                    await self.update_stage("synthesis", "running", progress=min(40 + i // 2, 95))
            except urllib.error.URLError:
                # Agent might be busy or restarting, wait and retry
                pass
            except Exception as e:
                # 404 is expected if job hasn't hit the dict yet, ignore other transitory errors
                logger.debug(f"[Stage 2.5] Polling notice (non-fatal): {e}")
                pass
        
        logger.warning("[Stage 2.5] Poll timeout - continuing anyway (Stage 3 has fallbacks).")

    # -------------------------------------------------------------------------
    # Stage 3 - Playwright Gen (real HTTP + fallback)
    # -------------------------------------------------------------------------
    async def _run_playwright_gen(self):
        import urllib.request, urllib.error
        import shutil

        # Phase 17 logic removed here - moved to _pre_pipeline_reset at start of run_pipeline
        pg_url  = os.getenv("PLAYWRIGHT_GEN_URL", "http://localhost:8002")
        job_id  = self.current_job_id
        logger.info(f"[Stage 3] Triggering Playwright Gen at {pg_url} ...")

        triggered = False
        try:
            body = json.dumps({"run_id": job_id}).encode()
            req  = urllib.request.Request(
                f"{pg_url}/generate/tests", data=body,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
                logger.info(f"Playwright Gen API response: {result}")
                triggered = True
        except Exception as e:
            logger.warning(f"Cannot reach port 8002: {e}. Using direct fallback.")

        if not triggered:
            await asyncio.get_event_loop().run_in_executor(None, self._run_generate_script_direct)
            return

        # Poll /job/{id} for completion
        for i in range(240):
            if self.aborted:
                raise InterruptedError()
            await asyncio.sleep(2)
            await self.update_stage("playwright_gen", "running", progress=min(10 + i // 4, 95))
            try:
                with urllib.request.urlopen(f"{pg_url}/job/{job_id}", timeout=5) as r:
                    d = json.loads(r.read())
                    st = d.get("status", "")
                    # v7.9: Fix keys to match playwright_gen/main.py
                    res = d.get("result", {})
                    met = res.get("metrics", {})
                    count = met.get("scripts_generated", met.get("pages_covered", 0))
                    
                    # Live update during polling
                    await self.update_stage("playwright_gen", "running", progress=min(10 + i // 2, 95), metrics={
                        "elements": count,
                        "finished": count
                    })

                    if st == "completed":
                        logger.info(f"[Stage 3] Done. {count} scripts generated.")
                        await self.update_stage("playwright_gen", "completed", progress=100, metrics={
                            "elements": count,
                            "finished": count
                        })
                        return
                    if st == "failed":
                        raise RuntimeError(f"Playwright Gen failed: {d.get('error')}")
            except urllib.error.HTTPError as e:
                # 404 is okay if agent hasn't started job status reporting yet
                if e.code != 404:
                    logger.debug(f"[Stage 3] HTTP {e.code} during poll")
                pass
            except Exception as e:
                logger.debug(f"[Stage 3] Exception during poll: {e}")
                pass

        logger.warning("[Stage 3] Poll timeout - running direct fallback.")
        await asyncio.get_event_loop().run_in_executor(None, self._run_generate_script_direct)

    def _run_generate_script_direct(self):
        """Run generate_script.py in-process when the API is not reachable."""
        import subprocess, os as _os
        pg_dir = CURRENT_DIR / "playwright_gen"
        logger.info("Running generate_script.py directly ...")
        # Pass current environment so .env API keys are available
        env = _os.environ.copy()
        r = subprocess.run(
            [sys.executable, "generate_script.py"],
            cwd=str(pg_dir), capture_output=True, text=True, timeout=480,
            env=env,
        )
        if r.returncode != 0:
            logger.error(f"generate_script.py failed:\n{r.stdout}\n{r.stderr}")
        else:
            logger.info("generate_script.py succeeded.")
            self._sync_tests_to_cicd()

    def _sync_tests_to_cicd(self):
        """Copy tests + config + testcases from playwright_gen -> cicd."""
        import shutil
        src_base = CURRENT_DIR / "playwright_gen"
        dst_base = CURRENT_DIR / "cicd"
        dst_base.mkdir(exist_ok=True)
        for folder in ("tests", "config", "testcases"):
            src = src_base / folder
            dst = dst_base / folder
            if src.exists():
                dst.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, dst, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                logger.info(f"Synced {folder}: {src} -> {dst}")

    # -------------------------------------------------------------------------
    # Stage 4 - Wait for Executor then Triage
    # -------------------------------------------------------------------------
    async def _wait_for_cicd(self):
        """Polls the CI/CD executor (port 8003) until the job finishes."""
        import urllib.request, json
        
        cicd_url = os.getenv("CICD_AGENT_URL", "http://localhost:8003")
        job_id   = self.current_job_id
        
        logger.info(f"[Stage 4] Waiting for CI/CD executor to finish job {job_id} ...")
        self.executor_metrics = {}

        for i in range(300):
            if self.aborted:
                raise InterruptedError()
            await asyncio.sleep(2)
            # Progress update for Execution stage
            try:
                with urllib.request.urlopen(f"{cicd_url}/job/{job_id}", timeout=5) as r:
                    d = json.loads(r.read())
                    st = d.get("status", "")
                    if st in ("completed", "failed"):
                        self.executor_metrics = d.get("result", {}).get("metrics", {})
                        logger.info(f"[Stage 4] Executor finished: {st} | metrics={self.executor_metrics}")
                        
                        # Set final metrics for Execution
                        passed = self.executor_metrics.get("passed", 0)
                        failed = self.executor_metrics.get("failed", 0)
                        await self.update_stage("cicd", "completed", progress=100, metrics={
                            "elements": passed + failed,
                            "finished": passed,
                            "passed": passed,
                            "failed": failed
                        })
                        return
                    else:
                        # Only update progress if not finished
                        await self.update_stage("cicd", "running", progress=min(5 + i // 4, 99))
            except Exception:
                # Still running or transitory error
                await self.update_stage("cicd", "running", progress=min(5 + i // 4, 95))
                pass
        
        logger.warning("[Stage 4] CICD Polling timeout.")

    async def _run_triage(self):
        """Trigger and poll for Triage analysis if execution had failures."""
        import urllib.request, json
        
        triage_url = os.getenv("TRIAGE_AGENT_URL", "http://localhost:8004")
        job_id     = self.current_job_id
        metrics    = getattr(self, "executor_metrics", {})
        failed_count = metrics.get("failed", 0)

        if failed_count <= 0:
            total = metrics.get("total_tests", "?")
            logger.info(f"[Stage 5] All {total} tests passed. Triage skipped.")
            await self.update_stage("triage", "completed", progress=100)
            return

        logger.info(f"[Stage 5] Triggering Triage for {failed_count} failure(s) ...")
        try:
            # Locate JUnit XML
            xml_path = CURRENT_DIR / "cicd" / "artifacts" / f"results_{job_id}.xml"
            if not xml_path.exists():
                xml_path = CURRENT_DIR / "cicd" / "artifacts" / "results.xml"

            stack = xml_path.read_text(encoding="utf-8", errors="ignore")[:5000] if xml_path.exists() else ""
            body  = json.dumps({
                "run_id":        job_id,
                "test_name":     f"CI/CD Suite - {failed_count} failures",
                "file_path":     str(xml_path),
                "error_message": f"{failed_count}/{metrics.get('total_tests', failed_count)} tests failed",
                "stack_trace":   stack,
                "logs":          "",
            }).encode()

            req = urllib.request.Request(
                f"{triage_url}/api/triage", data=body,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                res = json.loads(r.read())
                logger.info(f"[Stage 5] Triage triggered: {res.get('status')}")
            
            # Poll Triage Agent
            for j in range(60):
                if self.aborted:
                    raise InterruptedError()
                await asyncio.sleep(5)
                try:
                    with urllib.request.urlopen(f"{triage_url}/api/job/{job_id}", timeout=5) as r:
                        d = json.loads(r.read())
                        if d.get("status") == "completed":
                            logger.info(f"[Stage 5] Triage completed for job {job_id}")
                            await self.update_stage("triage", "completed", progress=100)
                            return
                        else:
                            # Only update progress if not finished
                            await self.update_stage("triage", "running", progress=min(10 + j // 2, 99))
                except Exception:
                    # Still running or transitory error
                    await self.update_stage("triage", "running", progress=min(10 + j // 2, 99))
                    pass
        except Exception as e:
            logger.error(f"[Stage 5] Triage failed (non-fatal): {e}")
            await self.update_stage("triage", "failed", error=str(e))

    # -------------------------------------------------------------------------
    # Control
    # -------------------------------------------------------------------------
    def stop(self):
        """Graceful abort."""
        logger.warning("Abort signal received.")
        self.aborted = True
        self.status["status"] = "aborted"
        self._save_status()


if __name__ == "__main__":
    logger.info("Starting Manual Orchestrator Test Run ...")
    orchestrator = PipelineOrchestrator()
    try:
        asyncio.run(orchestrator.run_pipeline("https://example.com", {}, "job_test_123"))
    except KeyboardInterrupt:
        logger.info("Exiting on KeyboardInterrupt")
    except Exception as e:
        logger.error(f"FATAL: {e}")

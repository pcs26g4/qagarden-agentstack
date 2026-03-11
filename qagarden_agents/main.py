import subprocess
import sys
import os
from dotenv import load_dotenv
# Load .env FIRST so GROQ_API_KEY is in os.environ before any subprocess is spawned
load_dotenv()
import asyncio
import httpx
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s | %(name)s | %(message)s"
)
logger = logging.getLogger("AgentStackMain")

# ─── Configuration ──────────────────────────────────────────────────
# SDK Wrapper URLs (Ports 9001-9005)
WRAPPERS = {
    "crawler":    "http://localhost:9001/v1/message:send",
    "testgen":    "http://localhost:9002/v1/message:send",
    "playwright": "http://localhost:9003/v1/message:send",
    "cicd":       "http://localhost:9004/v1/message:send",
    "triage":     "http://localhost:9005/v1/message:send"
}

# Backend URLs (Ports 8001-8005) for status polling
BACKENDS = {
    "crawler":    "http://localhost:8005",
    "testgen":    "http://localhost:8001",
    "playwright": "http://localhost:8002",
    "cicd":       "http://localhost:8003",
    "triage":     "http://localhost:8004"
}

import re

def launch_app(cwd, script, name, port):
    """Start process, but first check if port is already in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            logger.info(f"ℹ️ {name} is already running on port {port}. (Skipping restart)")
            return None

    logger.info(f"🚀 Starting {name} (Port {port})...")
    
    # In managed mode (Docker), log to stdout/stderr. Otherwise, use log files.
    if os.getenv("MANAGED_MODE") == "true":
        logger.info(f"📝 {name} is logging to console (MANAGED_MODE=true)")
        return subprocess.Popen(
            [sys.executable, script], 
            cwd=cwd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            bufsize=1, # Line buffered
            universal_newlines=True
        )

    # Redirect logs to <name>.log in the working directory
    log_name = re.sub(r'\W+', '_', name).lower() + ".log"
    log_file = open(os.path.join(cwd, log_name), "a", encoding="utf-8")
    
    return subprocess.Popen(
        [sys.executable, script], 
        cwd=cwd,
        stdout=log_file,
        stderr=log_file,
        bufsize=1, # Line buffered
        universal_newlines=True
    )

async def call_agent(url, message_id, payload):
    """Send A2A message and wait for the AgentStack task to complete."""
    data = {"message": {"messageId": message_id, "role": "ROLE_USER", "content": [{"text": json.dumps(payload)}]}}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=data)
        resp.raise_for_status()
        
        result_json = resp.json()
        task_id = result_json.get("task", {}).get("id")
        
        if not task_id:
            try: return result_json["message"]["content"][0]["text"]
            except (KeyError, IndexError): return json.dumps(result_json)
            
        # Extract base url from 'http://localhost:9001/v1/message:send' -> 'http://localhost:9001'
        base_wrapper_url = url.split("/v1/")[0]
        task_url = f"{base_wrapper_url}/v1/tasks/{task_id}"
        
        logger.info(f"   [AgentStack] Waiting for task {task_id} to finish...")
        for _ in range(120): # up to 10 minutes wait per agent
            await asyncio.sleep(5)
            try:
                task_resp = await client.get(task_url)
                if task_resp.status_code == 200:
                    task_data = task_resp.json()
                    state = task_data.get("status", {}).get("state", "")
                    
                    if state in ["TASK_STATE_COMPLETED", "TASK_STATE_FAILED", "TASK_STATE_CANCELLED"]:
                        history = task_data.get("history", [])
                        # Look for the last non-user message
                        for msg in reversed(history):
                            if msg.get("role") != "ROLE_USER":
                                try:
                                    text = msg["content"][0]["text"]
                                    if text: return text
                                except (KeyError, IndexError): pass
                        return json.dumps(task_data)
            except Exception as e:
                pass
                
        return f"❌ AgentStack Task {task_id} timed out."



async def run_pipeline(target_url, depth=10, pages=100):
    """The master automation loop."""
    run_id = f"auto_{datetime.now().strftime('%H%M%S')}"
    logger.info(f"🚀 PIPELINE STARTED: {run_id} for {target_url} (Depth: {depth}, Pages: {pages})")
    
    try:
        # 🟢 STAGE 1: CRAWL
        logger.info("📤 Sending Synchronous Trigger to Crawler Agent (Port 9001)...")
        payload = {
            "url": target_url,
            "max_depth": depth,
            "max_pages": pages, 
            "use_ai": True
        }
        resp_text = await call_agent(WRAPPERS["crawler"], f"c-{run_id}", payload)
        
        logger.info(f"📩 Agent Response Received ({len(resp_text)} chars)")

        if "❌" in resp_text:
            logger.error(f"🛑 Crawler Agent reported an error.")
            return
            
        # Extract Job ID from the final AgentStack response
        job_id = None
        try:
            # Look for the JSON block in the final response
            result_match = re.search(r"Full result:\s*(\{.*\})", resp_text, re.DOTALL)
            if result_match:
                try:
                    result_data = json.loads(result_match.group(1))
                    # Check root, then check common nested paths
                    job_id = (result_data.get("run_id") or 
                              result_data.get("job_id") or 
                              result_data.get("result", {}).get("job_id") or
                              result_data.get("last_update", {}).get("job_id"))
                except Exception:
                    pass
            
            # Fallback to search the whole text if still missing
            if not job_id:
                # Use a broader pattern for "Run ID" or "job_id"
                id_match = re.search(r"(?:Run ID|job_id)\s*:\s*([\w\-]+)", resp_text, re.IGNORECASE)
                if id_match:
                    job_id = id_match.group(1)
                else:
                    # Last ditch: try to find anything that looks like job_123456_X or a UUID
                    last_ditch = re.search(r"(job_\d+_\d+|[0-9a-f-]{36})", resp_text)
                    if last_ditch:
                        job_id = last_ditch.group(1)
        except Exception as e:
            logger.error(f"❌ Failed to parse Crawler response: {e}")

        if not job_id:
            logger.error(f"❌ Could not determine Job ID from Crawler response. Raw response:\n{resp_text}")
            return
            
        logger.info(f"📍 Synchronous success! Identified Job ID: {job_id}")


        # 🟢 STAGE 2: TEST GEN
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        domain = target_url.replace("https://", "").replace("http://", "").split("/")[0].replace(".", "_")
        locators = os.path.join(repo_root, "crawler", "locators_new", domain, "consolidated_locators.json")
        if not os.path.exists(locators):
            locators = os.path.join(repo_root, "crawler", "locators_old", "consolidated_locators.json")
            logger.info(f"⚠️  Consolidated locators fallback: {locators}")

        logger.info("📤 Sending Synchronous Trigger to TestGen Agent (Port 9002)...")
        resp_tg = await call_agent(WRAPPERS["testgen"], f"tg-{run_id}", {"run_id": job_id, "locators_path": locators})
        
        logger.info(f"📩 Agent Response Received ({len(resp_tg)} chars)")

        if "❌" in resp_tg:
            logger.error(f"🛑 Test Generator Agent reported an error.")
            return
            
        logger.info("📍 Synchronous success! Test cases generated.")


        # 🟢 STAGE 3: PLAYWRIGHT
        logger.info("📤 Sending Synchronous Trigger to Playwright Agent (Port 9003)...")
        resp_pw = await call_agent(WRAPPERS["playwright"], f"p-{run_id}", {"run_id": job_id})
        
        logger.info(f"📩 Agent Response Received ({len(resp_pw)} chars)")
        if "❌" in resp_pw:
            logger.error(f"🛑 Playwright Agent reported an error. Raw response:\n{resp_pw}")
            return
            
        logger.info("📍 Synchronous success! Playwright scripts generated.")

        # 🟢 STAGE 4: CICD
        logger.info("📤 Sending Synchronous Trigger to CICD Agent (Port 9004)...")
        resp_cicd = await call_agent(WRAPPERS["cicd"], f"cicd-{run_id}", {"run_id": job_id})
        
        logger.info(f"📩 Agent Response Received ({len(resp_cicd)} chars)")
        if "❌" in resp_cicd:
            logger.error(f"🛑 CICD Agent reported an error. Raw response:\n{resp_cicd}")
            return

        logger.info("📍 Synchronous success! CICD Pipeline tests executed.")

        # 🟢 STAGE 5: TRIAGE
        logger.info("📤 Sending Synchronous Trigger to Triage Agent (Port 9005)...")
        resp_triage = await call_agent(WRAPPERS["triage"], f"t-{run_id}", {"run_id": job_id, "test_name": "Full Suite"})
        
        logger.info(f"📩 Agent Response Received ({len(resp_triage)} chars)")
        if "❌" in resp_triage:
            logger.error(f"🛑 Triage Agent reported an error. Raw response:\n{resp_triage}")
            return

        logger.info(f"📍 Synchronous success! Triage analysis complete.")
        
        logger.info(f"🎉 PIPELINE COMPLETE: {run_id}")
    except Exception as e:
        logger.error(f"❌ Pipeline Execution Error: {e}")

async def main():
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(agent_dir)
    logger.info("Initializing AgentStack Full-Stack Ecosystem...")
    
    processes = []
    try:
        # 1. Launch Backends (800x)
        processes.append(launch_app(os.path.join(repo_root, "crawler"), "fastapi_endpoint.py", "Crawler BE", 8005))
        processes.append(launch_app(os.path.join(repo_root, "test_generator"), "main.py", "TestGen BE", 8001))
        processes.append(launch_app(os.path.join(repo_root, "playwright_gen"), "main.py", "Playwright BE", 8002))
        processes.append(launch_app(os.path.join(repo_root, "cicd"), "main.py", "CICD BE", 8003))
        processes.append(launch_app(os.path.join(repo_root, "triage_engine"), "main.py", "Triage BE", 8004))

        # 2. Launch Wrappers (900x)
        processes.append(launch_app(os.path.join(agent_dir, "src", "crawler_agent"), "server.py", "Crawler WR", 9001))
        processes.append(launch_app(os.path.join(agent_dir, "src", "test_generator_agent"), "server.py", "TestGen WR", 9002))
        processes.append(launch_app(os.path.join(agent_dir, "src", "playwright_agent"), "server.py", "Playwright WR", 9003))
        processes.append(launch_app(os.path.join(agent_dir, "src", "cicd_agent"), "server.py", "CICD WR", 9004))
        processes.append(launch_app(os.path.join(agent_dir, "src", "triage_engine_agent"), "server.py", "Triage WR", 9005))

        # Cleanup None values
        processes = [p for p in processes if p is not None]
        
        logger.info(f"Started {len(processes)} new services. Total ecosystem ports 8001-8005 & 9001-9005.")
        
        if "--run" in sys.argv:
            import argparse
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument("--run", type=str)
            parser.add_argument("--depth", type=int, default=10)
            parser.add_argument("--pages", type=int, default=100)
            
            # Use parse_known_args to avoid conflicts with sys.argv checks
            args, _ = parser.parse_known_args()
            
            url = args.run if args.run else "https://www.scrapethissite.com/"
            logger.info(f"Waiting 10s for services to be ready to run pipeline for: {url}")
            await asyncio.sleep(10) 
            await run_pipeline(url, depth=args.depth, pages=args.pages)
        else:
            logger.info("Wrappers are running. Use --run <url> to start an automated pipeline.")
            while True:
                await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down freshly started wrappers...")
        for p in processes: p.terminate()
        logger.info("Done.")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
from datetime import datetime
import websockets # Force check for websocket support
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Header
from typing import Dict, List, Optional
import os
import logging
import sys
from pathlib import Path

# Setup Logging FIRST before any other imports that may log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_endpoint")

import signal
import time
import traceback

def handle_exit_signal(sig, frame):
    try:
        sig_name = signal.Signals(sig).name
    except:
        sig_name = str(sig)
    
    logger.critical(f"PROCESS RECEIVED INTERRUPT: {sig_name} ({sig})")
    logger.critical("--- STACK TRACE ---")
    logger.critical("".join(traceback.format_stack()))
    logger.critical("-------------------")
    
    # We don't call sys.exit here to allow uvicorn's own signal handlers 
    # to handle the graceful shutdown.
    
signal.signal(signal.SIGTERM, handle_exit_signal)
signal.signal(signal.SIGINT, handle_exit_signal)

from config import CrawlerConfig
from qa_garden_crawler import QAGardenCrawler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Add parent dir for orchestrator import
sys.path.append(str(Path(__file__).parent.parent))
try:
    from orchestrator import PipelineOrchestrator
except ImportError as e:
    logger.warning(f"PipelineOrchestrator import failed: {e}")
    PipelineOrchestrator = None

app = FastAPI(title="QA Garden Phase-1 Crawler API")

# Enable CORS for the Dashboard (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev, or specify ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API Key Security (Load from .env in prod)
API_KEY = os.getenv("QA_GARDEN_API_KEY", "qa-garden-secret-key")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    logger.info("GROQ_API_KEY detected and injected into environment.")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    logger.info("GROQ_API_KEY detected and injected into environment.")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "online",
        "agent": "crawler",
        "version": "1.1.0",
        "timestamp": datetime.now().isoformat()
    }

# Lazy Global for Orchestrator to avoid asyncio.Event() loop errors at top-level
_pipeline_orchestrator = None

def get_orchestrator():
    global _pipeline_orchestrator
    if _pipeline_orchestrator is None and PipelineOrchestrator is not None:
        try:
            _pipeline_orchestrator = PipelineOrchestrator()
        except Exception as e:
            logger.error(f"Lazy PipelineOrchestrator init failed: {e}")
    return _pipeline_orchestrator
# Store active jobs, their progress queues, and crawler instances
jobs: Dict[str, Dict] = {}
job_queues: Dict[str, asyncio.Queue] = {}
job_instances: Dict[str, QAGardenCrawler] = {}
pipeline_job = None

@app.get("/")
def read_root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "QA Garden Crawler API is running."}

@app.post("/crawl")
async def start_crawl(config: CrawlerConfig, background_tasks: BackgroundTasks, x_api_key: str = Header(...)):
    """
    Trigger a new crawl job. Requires X-API-Key header.
    """
    # Log received key for diagnostics (masked)
    key_preview = f"{x_api_key[:4]}...{x_api_key[-4:]}" if len(x_api_key) > 8 else "***"
    logger.info(f"Incoming crawl request. URL: {config.url} | API Key: {key_preview}")
    
    if x_api_key != API_KEY:
        logger.error(f"API Key mismatch! Received: {key_preview}, Expected: {API_KEY[:4]}...{API_KEY[-4:]}")
        raise HTTPException(status_code=403, detail="Invalid API Key - Check your .env/api.ts config")
        
    # v10: Unique ID with timestamp to prevent clashing after restart
    run_id = f"job_{datetime.now().strftime('%H%M%S')}_{len(jobs) + 1}"
    config.job_id = run_id # Sync job ID
    
    jobs[run_id] = {"status": "starting", "config": config.dict()}
    job_queues[run_id] = asyncio.Queue()
    
    # Add to background tasks
    background_tasks.add_task(run_crawler_task, run_id, config)
    
    return {
        "run_id": run_id, # Changed from job_id to match frontend
        "status": "accepted",
        "message": "Crawl job started in background.",
        "locators_url": f"/job/{run_id}",
        "ws_url": f"/ws/{run_id}"
    }

@app.get("/job/{run_id}")
async def get_job_status(run_id: str):
    """
    Retrieve the status and configuration for a specific job.
    """
    if run_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {run_id} not found")
    return jobs[run_id]

@app.get("/jobs")
async def list_jobs():
    """
    List all crawl jobs and their current statuses.
    """
    return jobs

@app.post("/pause/{run_id}")
async def pause_run(run_id: str):
    """
    Pause an active crawl or pipeline run.
    """
    orch = get_orchestrator()
    if run_id.startswith("pipeline_"):
        if orch:
            orch.pause()
            return {"status": "paused", "run_id": run_id}
        raise HTTPException(status_code=400, detail="Pipeline orchestrator not initialized")
    
    if run_id not in job_instances:
        raise HTTPException(status_code=404, detail=f"Active run {run_id} not found")
    job_instances[run_id].pause_event.clear()
    return {"status": "paused", "run_id": run_id}

@app.post("/resume/{run_id}")
async def resume_run(run_id: str):
    """
    Resume a paused crawl or pipeline run.
    """
    orch = get_orchestrator()
    if run_id.startswith("pipeline_"):
        if orch:
            orch.resume()
            return {"status": "resumed", "run_id": run_id}
        raise HTTPException(status_code=400, detail="Pipeline orchestrator not initialized")

    if run_id not in job_instances:
        raise HTTPException(status_code=404, detail=f"Active run {run_id} not found")
    job_instances[run_id].pause_event.set()
    return {"status": "resumed", "run_id": run_id}

@app.post("/abort/{run_id}")
async def abort_run(run_id: str):
    """
    Abort an active crawl or pipeline run.
    """
    orch = get_orchestrator()
    if run_id.startswith("pipeline_"):
        if orch:
            orch.abort()
            return {"status": "aborting", "run_id": run_id}
        raise HTTPException(status_code=400, detail="Pipeline orchestrator not initialized")

    if run_id not in job_instances:
        raise HTTPException(status_code=404, detail="Active run not found")
    job_instances[run_id].abort_event.set()
    # Also resume it if it was paused to let it exit
    job_instances[run_id].pause_event.set()
    return {"status": "aborting", "run_id": run_id}

# Duplicate routes removed

# --- Pipeline Orchestration Endpoints ---

@app.post("/api/pipeline/start")
async def start_pipeline(config: CrawlerConfig, background_tasks: BackgroundTasks):
    """
    Triggers the full autonomous pipeline.
    """
    run_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Input Validation (Tweak from user)
    if not config.url or not config.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid Target URL")
    
    # Initialize queue for pipeline ID so UI can connect via WebSocket
    job_queues[run_id] = asyncio.Queue()
    jobs[run_id] = {"status": "starting", "config": config.dict()}

    orch = get_orchestrator()
    background_tasks.add_task(
        orch.run_pipeline, 
        config.url, 
        config.auth_creds or {}, 
        run_id,
        job_queues[run_id], # Pass the queue to the orchestrator for broadcasting
        config.max_depth,
        config.max_pages
    )
    
    return {
        "run_id": run_id,
        "status": "orchestrating",
        "message": "Full-stack pipeline triggered."
    }

@app.get("/api/pipeline/status")
async def pipeline_status_sse():
    """
    SSE endpoint for real-time pipeline updates.
    """
    orch = get_orchestrator()
    async def event_generator():
        while True:
            # Load from persistent JSON as requested
            status = {}
            if orch:
                status = orch.status
                if os.path.exists(orch.status_file):
                    try:
                        with open(orch.status_file, 'r') as f:
                            status = json.load(f)
                    except: pass
            
            yield f"data: {json.dumps(status)}\n\n"
            await asyncio.sleep(2) # Poll/Broadcast frequency
            
            if status.get("status") in ["completed", "failed", "aborted"]:
                # Send one last update then close
                yield f"data: {json.dumps(status)}\n\n"
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/pipeline/reset")
async def reset_pipeline():
    """
    Clears all job data and resets the orchestrator state.
    """
    # Clear in-memory state
    jobs.clear()
    job_queues.clear()
    job_instances.clear()
    
    # Reset Orchestrator state
    orch = get_orchestrator()
    if orch:
        orch.status = {
            "job_id": None,
            "status": "idle",
            "current_stage": None,
            "stages": {}
        }
        if os.path.exists(orch.status_file):
            try: os.remove(orch.status_file)
            except: pass
            
    return {"status": "reset", "message": "System state cleared."}

@app.post("/api/pipeline/stop")
async def stop_pipeline():
    """
    Aborts the running pipeline.
    """
    orch = get_orchestrator()
    if orch:
        orch.stop()
    return {"status": "aborting", "message": "Signal sent to orchestrator."}

from starlette.websockets import WebSocketState

@app.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection attempt for job: {run_id}")
    
    # If the job is already finished, send a final update and keep connection alive
    if run_id in jobs and jobs[run_id]["status"] in ["completed", "failed"]:
        logger.info(f"WebSocket: Job {run_id} already {jobs[run_id]['status']}. Sending final update.")
        await websocket.send_json(jobs[run_id].get("result") or {"status": jobs[run_id]["status"], "event": "completed", "agent": "crawler"})
        try:
            # Wait for client to disconnect
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            logger.info(f"WebSocket closed by client for finished job: {run_id}")
        return

    if run_id not in job_queues:
        # Fallback: if it's a pipeline run, auto-initialize the queue if it doesn't exist
        if run_id.startswith("pipeline_"):
            logger.info(f"Auto-initializing queue for pipeline: {run_id}")
            job_queues[run_id] = asyncio.Queue()
        else:
            logger.warning(f"WebSocket rejected: Job {run_id} not found in active queues.")
            await websocket.send_json({"event": "error", "message": f"Job {run_id} not found or expired. Please start a new run."})
            await websocket.close()
            return

    logger.info(f"WebSocket connected for job: {run_id}")
    
    # Send initial status  use real cached progress so UI doesn't reset to 0 on reconnect
    if run_id in jobs:
        job = jobs[run_id]
        # Pull the most recent metrics payload if available
        cached_metrics = job.get("metrics", {})
        initial_status = {
            "event": "progress",
            "agent": "crawler",
            "status": job["status"],
            "progress": job.get("progress", 0),
            "message": f"Connected to crawler (Status: {job['status']})",
            "config": job.get("config", {}),
            "metrics": cached_metrics,
        }
        await websocket.send_json(initial_status)
        logger.info(f"Sent initial WebSocket status for {run_id} (progress={initial_status['progress']})")


    try:
        while True:
            # Get next update from the job's queue
            update = await job_queues[run_id].get()
            
            # Map legacy 'completed' status to events if needed
            if "event" not in update:
                update["event"] = "progress"
                if update.get("status") in ["completed", "failed"]:
                    update["event"] = "completed"

            await websocket.send_json(update)
            
            if update.get("status") in ["completed", "failed"] and update.get("agent") == "pipeline":
                # Only keep-alive-indefinitely on FINAL pipeline completion
                logger.info(f"WebSocket: Pipeline {run_id} finished. Keeping alive.")
                while True:
                    await websocket.receive_text()
            elif update.get("event") == "completed":
                # Logic to keep alive slightly for stage handovers if needed
                logger.debug(f"WebSocket: Stage {update.get('agent')} completed.")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job: {run_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {run_id}: {e}", exc_info=True)
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except:
                pass

async def run_crawler_task(run_id: str, config: CrawlerConfig):
    try:
        # Send initial starting message to queue
        if run_id in job_queues:
            await job_queues[run_id].put({
                "event": "log",
                "agent": "crawler",
                "status": "starting",
                "level": "info",
                "message": f"Autonomous agent {run_id} initialized and preparing to launch..."
            })
            await job_queues[run_id].put({
                "event": "progress",
                "agent": "crawler",
                "status": "running",
                "progress": 5,
                "message": "Initializing browser session...",
                "config": config.dict()
            })

        crawler = QAGardenCrawler(config)
        job_instances[run_id] = crawler # Store instance for control
        jobs[run_id]["status"] = "in_progress"
        
        # We iterate through the generator to get updates
        first_update = True
        async for update in crawler.run():
            # Inject metrics from the event payload (already populated by the crawler)
            if update.get("event") == "progress":
                # Use metrics already embedded by qa_garden_crawler.py
                # Fallback: compute from finished_urls if metrics not present
                if "metrics" not in update:
                    _finished = len(crawler.finished_urls)
                    _discovered = len(crawler.discovery_queue)
                    update["metrics"] = {
                        "elements": _finished,
                        "discovered": _discovered,
                        "finished": _finished,
                        "current_url": update.get("url", ""),
                        "coverage": round((_finished / (crawler.config.max_pages or 50)) * 100, 1)
                    }
                if first_update:
                    update["config"] = jobs[run_id]["config"]
                    first_update = False
                
                # Persist latest progress + metrics so reconnecting WebSocket clients see accurate state
                jobs[run_id]["progress"] = update.get("progress", 0)
                jobs[run_id]["metrics"] = update.get("metrics", {})

            jobs[run_id]["last_update"] = update

            
            # Put update into queue for WebSocket subscribers
            if run_id in job_queues:
                await job_queues[run_id].put(update)
            
            if update.get("status") == "completed":
                # Inject correct path
                update["path"] = os.path.abspath(os.path.join(crawler.locators_dir, "consolidated_locators.json")) if hasattr(crawler, "locators_dir") else ""
                logger.info(f"Injecting absolute file path into completion event: {update['path']}")

                jobs[run_id]["status"] = "completed"
                jobs[run_id]["result"] = update
                
    except Exception as e:
        logger.error(f"Crawler job {run_id} failed: {e}")
        jobs[run_id]["status"] = "failed"
        jobs[run_id]["error"] = str(e)
        if run_id in job_queues:
            await job_queues[run_id].put({"status": "failed", "event": "completed", "error": str(e)})
    finally:
        # Final safety check: if we didn't send a completed/failed status, send one now
        if jobs.get(run_id, {}).get("status") not in ["completed", "failed"]:
            status = "completed" # Assume completed if reached end without exception
            final_msg = {
                "status": status, 
                "event": "completed", 
                "agent": "crawler", 
                "message": "Task ended."
            }
            # Include locators path for handover (use absolute path)
            if 'crawler' in locals() and hasattr(crawler, 'locators_root'):
                abs_path = os.path.abspath(os.path.join(crawler.locators_root, 'consolidated_locators.json'))
                final_msg["path"] = abs_path
                logger.info(f"Injecting absolute file path into completion: {abs_path}")
                
            # PERSIST the status so periodic polling sees it!
            jobs[run_id]["status"] = status
            if run_id in job_queues:
                await job_queues[run_id].put(final_msg)
        
        if run_id in job_instances:
            del job_instances[run_id]

def print_banner(port):
    import socket
    import sys
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_ip = s.getsockname()[0]
        s.close()
    except Exception:
        network_ip = "127.0.0.1"
    banner = f"""
{'='*50}
 Crawler Agent - Swagger UI:
   Local:   http://localhost:{port}/docs
   Network: http://{network_ip}:{port}/docs
{'='*50}
"""
    print(banner, file=sys.stderr, flush=True)

if __name__ == "__main__":
    import uvicorn
    print_banner(8005)
    uvicorn.run(app, host="0.0.0.0", port=8005)


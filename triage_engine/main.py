import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.routes import router as api_router

# Load environment variables from multiple candidates
from pathlib import Path
_THIS_DIR = Path(__file__).resolve().parent
for _candidate in [
    _THIS_DIR / ".env",
    _THIS_DIR.parent / ".env",
    _THIS_DIR.parent / "qagarden_agents" / ".env",
]:
    if _candidate.exists():
        load_dotenv(dotenv_path=_candidate, override=True)
        break
else:
    load_dotenv()

app = FastAPI(title="Bug Triage Engine")

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
if "*" not in origins:
    origins.append("*")  # Fallback for development flexibility

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "triage_engine"}

# ── Orchestrator compatibility shims ─────────────────────────────────
# The orchestrator polls /jobs and /job/{run_id} at the root.
# We delegate these to the storage_service directly.
from app.services import storage_service

@app.get("/jobs")
def list_jobs_compat():
    results = storage_service.get_all_results()
    jobs_map = {}
    for r in results:
        rid = r.get("run_id", r.get("id", "unknown"))
        jobs_map[rid] = {"status": "completed", "run_id": rid}
    return jobs_map

@app.get("/job/{run_id}")
async def get_job_compat(run_id: str):
    status = storage_service.get_run_status(run_id)
    results = storage_service.get_results_by_run_id(run_id)
    return {
        "status": status,
        "run_id": run_id,
        "results_count": len(results)
    }


# WebSocket Endpoint
from fastapi import WebSocket, WebSocketDisconnect
from app.socket_manager import manager

@app.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await manager.connect(websocket, run_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, run_id)

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
 Triage Engine - Swagger UI:
   Local:   http://localhost:{port}/docs
   Network: http://{network_ip}:{port}/docs
{'='*50}
"""
    print(banner, file=sys.stderr, flush=True)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("TRIAGE_ENGINE_PORT", 8004))
    
    print_banner(port)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )



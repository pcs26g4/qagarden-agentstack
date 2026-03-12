"""
AgentStack SDK wrapper for the QA Garden Triage Engine Agent.
Upstream Port: 8004
"""
import json
import os
import httpx
import asyncio
from a2a.types import Message
from a2a.utils.message import get_message_text
from agentstack_sdk.a2a.types import AgentMessage
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

BASE_URL = os.getenv("TRIAGE_ENGINE_URL", "http://127.0.0.1:8004")
server = Server()

@server.agent()
async def triage_agent(input: Message, context: RunContext):
    raw_message = get_message_text(input).strip()
    
    payload: dict = {}
    try:
        payload = json.loads(raw_message)
    except (json.JSONDecodeError, ValueError):
        payload = {"error_message": raw_message}

    # Ensure required fields for Triage Engine's FailureInput schema are present
    # This prevents '422 Unprocessable Entity' errors when triggered with partial data
    payload.setdefault("test_name", "Orchestrator Trigger")
    payload.setdefault("file_path", "main.py")
    payload.setdefault("stack_trace", "Triggered by full pipeline orchestrator.")
    if "error_message" not in payload and "run_id" in payload:
        payload["error_message"] = f"Manual triage trigger for run {payload['run_id']}"
    payload.setdefault("error_message", "Manual triage request.")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{BASE_URL}/api/triage", json=payload)
            response.raise_for_status()
            result = response.json()
    except Exception as e:
        yield AgentMessage(text=f"❌ Error calling Triage Engine: {str(e)}")
        return

    # ── Wait for the job to complete (Internal Polling) ────────────
    run_id = payload.get("run_id")
    if run_id:
        status_url = f"{BASE_URL}/job/{run_id}"
        is_done = False
        
        # Poll every 5 seconds for up to 60 minutes
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(720):
                try:
                    status_resp = await client.get(status_url)
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        status = status_data.get("status", "").lower()
                        
                        if status in ["completed", "success", "finished"]:
                            is_done = True
                            break
                        if status in ["failed", "error"]:
                            yield AgentMessage(text=f"❌ Triage job {run_id} failed on the backend.")
                            return
                except Exception:
                    pass
                await asyncio.sleep(5)

        if not is_done:
            yield AgentMessage(text=f"❌ Timeout waiting for Triage job {run_id} to complete after 60 minutes.")
            return

    yield AgentMessage(text=f"✅ Triage complete!\n\nResponse: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    server.run(host=host, port=9005)

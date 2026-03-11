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

BASE_URL = os.getenv("CICD_URL", "http://127.0.0.1:8003")
server = Server()

@server.agent()
async def cicd_agent(input: Message, context: RunContext):
    raw_message = get_message_text(input).strip()
    
    payload: dict = {}
    try:
        payload = json.loads(raw_message)
    except (json.JSONDecodeError, ValueError):
        payload = {"run_id": raw_message}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{BASE_URL}/generate/tests", json=payload)
            response.raise_for_status()
            result = response.json()
    except Exception as e:
        yield AgentMessage(text=f"❌ Error calling CICD Agent: {str(e)}")
        return

    # ── Wait for the job to complete (Internal Polling) ────────────
    run_id = payload.get("run_id")
    status_url = f"{BASE_URL}/job/{run_id}"
    is_done = False
    
    # Poll every 5 seconds for up to 10 minutes
    async with httpx.AsyncClient(timeout=10.0) as client:
        for _ in range(120):
            try:
                status_resp = await client.get(status_url)
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    status = status_data.get("status", "").lower()
                    
                    if status in ["completed", "success", "finished"]:
                        is_done = True
                        result = status_data
                        break
                    if status in ["failed", "error"]:
                        yield AgentMessage(text=f"❌ CICD job {run_id} failed on the backend.")
                        return
            except Exception:
                pass
            await asyncio.sleep(5)

    if not is_done:
        yield AgentMessage(text=f"❌ Timeout waiting for CICD job {run_id} to complete.")
        return

    # ── Return the FINAL result ────────────────────────────────────
    report_path = result.get("report_path", "unknown")

    summary = (
        f"✅ CICD Test Execution COMPLETED!\n\n"
        f"  Run ID  : {run_id}\n"
        f"  Report  : {report_path}\n\n"
        f"Full result: {json.dumps(result, indent=2)}"
    )
    yield AgentMessage(text=summary)

if __name__ == "__main__":
    server.run(host="127.0.0.1", port=9004)
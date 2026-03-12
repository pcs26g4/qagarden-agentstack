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

# ─── Configuration ──────────────────────────────────────────────────
# The Test Generator backend is typically on port 8001 (from main.py)
TEST_GEN_BASE_URL = os.getenv("TEST_GEN_URL", "http://127.0.0.1:8001")
WRAPPER_HOST      = os.getenv("HOST", "0.0.0.0")
WRAPPER_PORT      = int(os.getenv("PORT", "9002"))

# ─── AgentStack Server ───────────────────────────────────────────────
server = Server()

@server.agent()
async def test_generator_agent(input: Message, context: RunContext):
    """
    AgentStack wrapper for the QA Garden Test Generator Agent.

    Accepts a JSON message with:
    - run_id: The ID from the crawler run.
    - locators_path: Absolute path to the crawler's locator JSON file.
    - target_url: (Optional) The original base URL.
    """
    raw_message = get_message_text(input).strip()

    # ── Parse the incoming message ─────────────────────────────────
    payload: dict = {}
    try:
        payload = json.loads(raw_message)
    except (json.JSONDecodeError, ValueError):
        yield AgentMessage(
            text="❌ Error: Test Generator expects a JSON payload with 'run_id' and 'locators_path'."
        )
        return

    # ── Validation ─────────────────────────────────────────────────
    if not payload.get("run_id") or not payload.get("locators_path"):
        yield AgentMessage(
            text="❌ Error: Missing 'run_id' or 'locators_path' in request."
        )
        return

    # ── Call the upstream Test Generator FastAPI service ───────────
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, check health
            health = await client.get(f"{TEST_GEN_BASE_URL}/health")
            health.raise_for_status()

            # Submit the generation job (matches CrawlerHandoverRequest)
            # Use /api/v1/generate-tests endpoint
            response = await client.post(
                f"{TEST_GEN_BASE_URL}/api/v1/generate-tests",
                json=payload
            )
            response.raise_for_status()
            result = response.json()

    except httpx.ConnectError:
        yield AgentMessage(
            text=(
                f"❌ Cannot connect to test generator service at {TEST_GEN_BASE_URL}. "
                "Make sure the Test Generator FastAPI server is running."
            )
        )
        return
    except httpx.HTTPStatusError as exc:
        yield AgentMessage(
            text=f"❌ Test Generator service returned error {exc.response.status_code}: "
                 f"{exc.response.text}"
        )
        return

    # ── Wait for the job to complete (Internal Polling) ────────────
    run_id = payload.get("run_id")
    status_url = f"{TEST_GEN_BASE_URL}/api/v1/job/{run_id}"
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
                        result = status_data
                        break
                    if status in ["failed", "error"]:
                        yield AgentMessage(text=f"❌ Test generation job {run_id} failed on the backend.")
                        return
            except Exception:
                pass
            await asyncio.sleep(5)

    if not is_done:
        yield AgentMessage(text=f"❌ Timeout waiting for test generation job {run_id} to complete after 60 minutes.")
        return

    # ── Return the FINAL result ────────────────────────────────────
    count = result.get("testCaseCount", 0)
    model = result.get("modelUsed", "unknown")

    summary = (
        f"✅ Test generation COMPLETED!\n\n"
        f"  Run ID  : {run_id}\n"
        f"  Count   : {count} test cases\n"
        f"  Model   : {model}\n\n"
        f"Full result: {json.dumps(result, indent=2)}"
    )
    yield AgentMessage(text=summary)


# ─── Entry point ─────────────────────────────────────────────────────
def run():
    print(f"Starting Test Generator Agent Wrapper on {WRAPPER_HOST}:{WRAPPER_PORT}...")
    server.run(host=WRAPPER_HOST, port=WRAPPER_PORT)

if __name__ == "__main__":
    run()

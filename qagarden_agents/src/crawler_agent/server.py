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
CRAWLER_BASE_URL = os.getenv("CRAWLER_URL", "http://127.0.0.1:8005")
WRAPPER_HOST     = os.getenv("HOST", "0.0.0.0")
WRAPPER_PORT     = int(os.getenv("PORT", "9001"))
QA_GARDEN_API_KEY = os.getenv("QA_GARDEN_API_KEY", "qa-garden-secret-key")

# ─── AgentStack Server ───────────────────────────────────────────────
server = Server()

@server.agent()
async def crawler_agent(input: Message, context: RunContext):
    """
    AgentStack wrapper for the QA Garden Crawler Agent.

    Accepts a natural-language or JSON message containing a URL to crawl.
    ...
    """
    raw_message = get_message_text(input).strip()

    # ── Parse the incoming message ─────────────────────────────────
    crawl_payload: dict = {}
    try:
        parsed = json.loads(raw_message)
        if isinstance(parsed, dict):
            crawl_payload = parsed
        else:
            crawl_payload = {"url": str(parsed)}
    except (json.JSONDecodeError, ValueError):
        crawl_payload = {"url": raw_message}

    if not crawl_payload.get("url"):
        yield AgentMessage(
            text="❌ Error: No URL provided."
        )
        return

    # ── Set sensible defaults ──────────────────────────────────────
    crawl_payload.setdefault("max_depth", 10)
    crawl_payload.setdefault("max_pages", 100)

    # ── Call the upstream crawler FastAPI service ──────────────────
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, confirm the crawler is healthy
            health = await client.get(f"{CRAWLER_BASE_URL}/health")
            health.raise_for_status()

            # Submit the crawl job with required API Key
            response = await client.post(
                f"{CRAWLER_BASE_URL}/crawl",
                json=crawl_payload,
                headers={"X-API-Key": QA_GARDEN_API_KEY}
            )
            response.raise_for_status()
            result = response.json()

    except httpx.ConnectError:
        yield AgentMessage(
            text=(
                f"❌ Cannot connect to crawler service at {CRAWLER_BASE_URL}. "
                "Make sure the crawler FastAPI server is running:\n"
                "  cd d:\\agentstack\\qagarden && python main.py"
            )
        )
        return
    except httpx.HTTPStatusError as exc:
        yield AgentMessage(
            text=f"❌ Crawler service returned error {exc.response.status_code}: "
                 f"{exc.response.text}"
        )
        return

    # ── Wait for the job to complete (Internal Polling) ────────────
    run_id = result.get("run_id", "unknown")
    
    status_url = f"{CRAWLER_BASE_URL}/job/{run_id}"
    is_done = False
    
    # Poll every 5 seconds for up to 60 minutes
    async with httpx.AsyncClient(timeout=10.0) as client:
        for _ in range(720): 
            try:
                status_resp = await client.get(status_url)
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    current_status = status_data.get("status", "").lower()
                    
                    if current_status in ["completed", "success", "finished"]:
                        is_done = True
                        result = status_data # Update result with final data
                        break
                    if current_status in ["failed", "error"]:
                        yield AgentMessage(text=f"❌ Crawler job {run_id} failed on the backend.")
                        return
                
            except Exception:
                # Silently continue polling
                pass
            
            await asyncio.sleep(5)

    if not is_done:
        yield AgentMessage(text=f"❌ Timeout waiting for crawler job {run_id} to complete after 60 minutes.")
        return

    # ── Return the FINAL result ────────────────────────────────────
    status   = result.get("status", "completed")
    locators_url = result.get("locators_url", f"/job/{run_id}")
    job_url  = f"{CRAWLER_BASE_URL}{locators_url}"
    
    # We yield a message that includes the final data for the next agent
    summary = (
        f"✅ Crawl job COMPLETED!\n\n"
        f"  Run ID  : {run_id}\n"
        f"  URL     : {crawl_payload['url']}\n"
        f"  Locators: {job_url}\n\n"
        f"Full result: {json.dumps(result, indent=2)}"
    )
    yield AgentMessage(text=summary)


# ─── Entry point ─────────────────────────────────────────────────────
def run():
    server.run(host=WRAPPER_HOST, port=WRAPPER_PORT)

if __name__ == "__main__":
    run()
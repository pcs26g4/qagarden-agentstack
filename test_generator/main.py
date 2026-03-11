"""Root entry point shim for Test Generator.
This file allows the orchestrator to find main.py at the root while 
keeping the internal code in the 'app/' directory functional.
"""
import os
import sys

# Add the current directory to sys.path so 'app' module is correctly discovered
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.main import app
from app.core.config import settings
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("TEST_GENERATOR_PORT", 8001))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False, # Disable reload for production/orchestrator stability
        log_level="info"
    )

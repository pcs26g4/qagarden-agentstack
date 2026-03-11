import subprocess
import sys
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s")
logger = logging.getLogger("SystemLauncher")

def start_agent(base_dir, agent_folder, script_name):
    agent_dir = os.path.join(base_dir, agent_folder)
    logger.info(f"Starting {agent_folder} [{script_name}]...")
    
    # Run using the exact current Python interpreter driving main.py
    # Assumes dependencies are installed globally in the running interpreter
    return subprocess.Popen(
        [sys.executable, script_name], 
        cwd=agent_dir
    )

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info("Initializing QA Garden API Backend Ecosystem...")
    
    processes = []
    try:
        # Launch 5 core independent agent processes simultaneously
        processes.append(start_agent(base_dir, "crawler", "fastapi_endpoint.py"))
        processes.append(start_agent(base_dir, "test_generator", "main.py"))
        processes.append(start_agent(base_dir, "playwright_gen", "main.py"))
        processes.append(start_agent(base_dir, "cicd", "main.py"))
        processes.append(start_agent(base_dir, "triage_engine", "main.py"))
        
        logger.info("All 5 agents successfully started! Ecosystem is online.")
        logger.info("Press Ctrl+C to gracefully terminate the entire ecosystem.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\nTermination signal received. Shutting down all agents gracefully...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        logger.info("All agents safely terminated. Goodbye.")

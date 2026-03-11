"""Server-Sent Events (SSE) manager for broadcasting updates to connected clients."""
import asyncio
import json
from typing import Set, Dict, Optional
from app.core.logger import app_logger


class SSEManager:
    """Manages SSE connections and broadcasts messages to specific run IDs."""
    
    def __init__(self):
        # Map run_id -> set of asyncio.Queue
        self.run_connections: dict[str, Set[asyncio.Queue]] = {}
    
    async def connect(self, run_id: str) -> asyncio.Queue:
        """
        Create a new SSE connection for a specific run.
        
        Args:
            run_id: The ID of the run to connect to
            
        Returns:
            Queue for sending messages to this client
        """
        queue = asyncio.Queue()
        if run_id not in self.run_connections:
            self.run_connections[run_id] = set()
        self.run_connections[run_id].add(queue)
        
        total_conns = sum(len(conns) for conns in self.run_connections.values())
        app_logger.info(f"New SSE connection for run {run_id}. Run connections: {len(self.run_connections[run_id])}, Total: {total_conns}")
        return queue
    
    async def disconnect(self, run_id: str, queue: asyncio.Queue):
        """
        Remove an SSE connection.
        
        Args:
            run_id: The ID of the run
            queue: Queue to remove
        """
        if run_id in self.run_connections and queue in self.run_connections[run_id]:
            self.run_connections[run_id].remove(queue)
            if not self.run_connections[run_id]:
                self.run_connections.pop(run_id, None)
            
            total_conns = sum(len(conns) for conns in self.run_connections.values())
            app_logger.info(f"SSE connection closed for run {run_id}. Total: {total_conns}")
    
    async def broadcast(self, event_type: str, data: dict, run_id: Optional[str] = None):
        """
        Broadcast a message to connected clients.
        
        Args:
            event_type: Type of event (e.g., 'test_cases_updated')
            data: Data to send
            run_id: Optional run ID to filter by. If None, broadcasts to everyone (use sparingly).
        """
        message = {
            "type": event_type,
            "data": data
        }
        message_json = json.dumps(message)
        
        target_run_ids = [run_id] if run_id else list(self.run_connections.keys())
        
        for rid in target_run_ids:
            if rid not in self.run_connections:
                continue
                
            dead_connections = set()
            for queue in self.run_connections[rid]:
                try:
                    await queue.put(message_json)
                except Exception as e:
                    app_logger.warning(f"Error sending SSE message for run {rid}: {str(e)}")
                    dead_connections.add(queue)
            
            # Remove dead connections
            for queue in dead_connections:
                self.run_connections[rid].discard(queue)
            
            if not self.run_connections[rid]:
                self.run_connections.pop(rid, None)

        app_logger.info(f"Broadcasted '{event_type}' to run {run_id if run_id else 'ALL'}")
    
    def get_connection_count(self, run_id: Optional[str] = None) -> int:
        """Get the number of active connections."""
        if run_id:
            return len(self.run_connections.get(run_id, set()))
        return sum(len(conns) for conns in self.run_connections.values())


# Global SSE manager instance
sse_manager = SSEManager()


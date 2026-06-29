import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("nomen.websocket")

class WebSocketConnectionManager:
    """Manages active WebSocket connections grouped by user and workspace.
    
    Supports:
      - Authenticating connections.
      - Presence tracking.
      - Workspace-wide broadcasting.
      - Direct user notifying.
    """
    
    def __init__(self):
        # Maps workspace_id -> Set of active user_ids
        self.workspace_presence: Dict[str, Set[str]] = {}
        # Maps user_id -> List of active WebSocket objects
        self.user_connections: Dict[str, List[WebSocket]] = {}
        # Maps workspace_id -> List of active WebSocket objects
        self.workspace_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, workspace_id: str):
        """Accepts connection, registers details, and broadcasts updated workspace presence."""
        await websocket.accept()
        
        user_str = str(user_id)
        ws_str = str(workspace_id)
        
        # 1. Register user connections
        if user_str not in self.user_connections:
            self.user_connections[user_str] = []
        self.user_connections[user_str].append(websocket)
        
        # 2. Register workspace connections
        if ws_str not in self.workspace_connections:
            self.workspace_connections[ws_str] = []
        self.workspace_connections[ws_str].append(websocket)
        
        # 3. Track presence
        if ws_str not in self.workspace_presence:
            self.workspace_presence[ws_str] = set()
        self.workspace_presence[ws_str].add(user_str)
        
        logger.info(f"WebSocket connected. User: {user_str}, Workspace: {ws_str}")
        
        # Broadcast updated presence list to workspace members
        await self.broadcast_presence(ws_str)

    async def disconnect(self, websocket: WebSocket, user_id: str, workspace_id: str):
        """Removes client references and broadcasts updated workspace presence."""
        user_str = str(user_id)
        ws_str = str(workspace_id)
        
        # 1. Remove from user connections list
        if user_str in self.user_connections:
            if websocket in self.user_connections[user_str]:
                self.user_connections[user_str].remove(websocket)
            if not self.user_connections[user_str]:
                del self.user_connections[user_str]
                
        # 2. Remove from workspace connections list
        if ws_str in self.workspace_connections:
            if websocket in self.workspace_connections[ws_str]:
                self.workspace_connections[ws_str].remove(websocket)
            if not self.workspace_connections[ws_str]:
                del self.workspace_connections[ws_str]
                
        # 3. Update presence
        # Only remove from presence set if the user has no remaining active sockets in this workspace
        user_has_sockets = False
        if ws_str in self.workspace_connections and user_str in self.user_connections:
            for ws_socket in self.workspace_connections[ws_str]:
                if ws_socket in self.user_connections[user_str]:
                    user_has_sockets = True
                    break
        
        if not user_has_sockets and ws_str in self.workspace_presence:
            if user_str in self.workspace_presence[ws_str]:
                self.workspace_presence[ws_str].remove(user_str)
            if not self.workspace_presence[ws_str]:
                del self.workspace_presence[ws_str]
                
        logger.info(f"WebSocket disconnected. User: {user_str}, Workspace: {ws_str}")
        
        # Broadcast updated presence
        await self.broadcast_presence(ws_str)

    async def broadcast_to_workspace(self, workspace_id: str, event: str, data: dict):
        """Sends an event payload to all active members of a workspace."""
        ws_str = str(workspace_id)
        if ws_str not in self.workspace_connections:
            return
            
        payload = json.dumps({"event": event, "data": data})
        disconnected_sockets = []
        
        for connection in self.workspace_connections[ws_str]:
            try:
                await connection.send_text(payload)
            except Exception:
                disconnected_sockets.append(connection)
                
        # Clean up dead sockets
        for dead_socket in disconnected_sockets:
            self.workspace_connections[ws_str].remove(dead_socket)

    async def send_to_user(self, user_id: str, event: str, data: dict):
        """Sends an event payload directly to all active connection sockets of a user."""
        user_str = str(user_id)
        if user_str not in self.user_connections:
            return
            
        payload = json.dumps({"event": event, "data": data})
        disconnected_sockets = []
        
        for connection in self.user_connections[user_str]:
            try:
                await connection.send_text(payload)
            except Exception:
                disconnected_sockets.append(connection)
                
        # Clean up dead sockets
        for dead_socket in disconnected_sockets:
            self.user_connections[user_str].remove(dead_socket)

    async def broadcast_presence(self, workspace_id: str):
        """Helper to broadcast current presence list of active member user IDs in a workspace."""
        ws_str = str(workspace_id)
        presence_list = list(self.workspace_presence.get(ws_str, set()))
        await self.broadcast_to_workspace(
            workspace_id=ws_str,
            event="presence",
            data={"active_users": presence_list}
        )

# Global manager instance
manager = WebSocketConnectionManager()

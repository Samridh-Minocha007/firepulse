# firepulse/services/connection_manager.py
from fastapi import WebSocket
from typing import List, Dict, Tuple

class ConnectionManager:
    def __init__(self):
        # The key is party_id, and the value is a list of (user_id, websocket) tuples
        self.active_connections: Dict[str, List[Tuple[str, WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, party_id: str, user_id: str):
        """Accepts a new WebSocket connection and adds it to the party with the user_id."""
        await websocket.accept()
        if party_id not in self.active_connections:
            self.active_connections[party_id] = []
        self.active_connections[party_id].append((user_id, websocket))

    def disconnect(self, websocket: WebSocket, party_id: str):
        """Removes a WebSocket connection from a party."""
        if party_id in self.active_connections:
            connection_to_remove = None
            for conn_tuple in self.active_connections[party_id]:
                if conn_tuple[1] == websocket:
                    connection_to_remove = conn_tuple
                    break
            if connection_to_remove:
                self.active_connections[party_id].remove(connection_to_remove)

    async def broadcast(self, message: str, party_id: str):
        """Sends a message to all clients in a specific party."""
        if party_id in self.active_connections:
            for user_id, connection in self.active_connections[party_id]:
                await connection.send_text(message)

    def get_users_in_party(self, party_id: str) -> List[str]:
        """Returns a list of user_ids for all users in a party."""
        if party_id in self.active_connections:
            return [user_id for user_id, ws in self.active_connections[party_id]]
        return []

manager = ConnectionManager()
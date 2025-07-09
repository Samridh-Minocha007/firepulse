from fastapi import WebSocket
from typing import List, Dict, Tuple

class ConnectionManager:
    def __init__(self):
       
        self.active_connections: Dict[str, List[Tuple[str, WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, party_id: str, user_id: str):
        
        await websocket.accept()
        if party_id not in self.active_connections:
            self.active_connections[party_id] = []
        self.active_connections[party_id].append((user_id, websocket))

    def disconnect(self, websocket: WebSocket, party_id: str):
        
        if party_id in self.active_connections:
            connection_to_remove = None
            for conn_tuple in self.active_connections[party_id]:
                if conn_tuple[1] == websocket:
                    connection_to_remove = conn_tuple
                    break
            if connection_to_remove:
                self.active_connections[party_id].remove(connection_to_remove)

    async def broadcast(self, message: str, party_id: str):
        
        if party_id in self.active_connections:
            for user_id, connection in self.active_connections[party_id]:
                await connection.send_text(message)

    def get_users_in_party(self, party_id: str) -> List[str]:
        
        if party_id in self.active_connections:
            return [user_id for user_id, ws in self.active_connections[party_id]]
        return []

manager = ConnectionManager()
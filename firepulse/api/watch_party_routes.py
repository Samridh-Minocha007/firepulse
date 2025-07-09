from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import httpx
from ..services.connection_manager import manager
from ..services import group_recs
from ..core.db import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws/{party_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, party_id: str, user_id: str, db: Session = Depends(get_db)):
    """
    Handles the WebSocket connection for a user in a specific watch party.
    NOTE: user_id here is treated as the user's email for simplicity.
    """
    await manager.connect(websocket, party_id, user_id)
    await manager.broadcast(f"User '{user_id}' has joined the party.", party_id)

    client: httpx.AsyncClient = websocket.app.state.httpx_client

    try:
        while True:
            data = await websocket.receive_text()

            
            if data == "suggest_movie":
                await manager.broadcast("Finding a movie for the group...", party_id)
                user_ids_in_party = manager.get_users_in_party(party_id)
                suggestion = await group_recs.suggest_movie_for_group(db, client, user_ids_in_party)
                await manager.broadcast(f"Suggestion for the group: {suggestion}", party_id)
            else:
               
                await manager.broadcast(f"{user_id}: {data}", party_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, party_id)
        await manager.broadcast(f"User '{user_id}' has left the party.", party_id)


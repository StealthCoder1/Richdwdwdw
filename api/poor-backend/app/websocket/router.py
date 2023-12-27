from fastapi import APIRouter, WebSocket

from app.websocket.connection_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client = await manager.connect(websocket)

    await client.loop()

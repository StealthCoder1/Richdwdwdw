from typing import Any

from fastapi import WebSocket

from app.auth.jwt import parse_jwt_user_data_optional
from app.websocket.schemas import Message


class Client:
    def __init__(self, manager: "ConnectionManager", ws: WebSocket) -> None:
        self.manager = manager
        self.ws = ws
        self.user_id: int = None

    async def on_connect(self):
        await self.ws.accept()

    async def on_event(self, event: str, data: Any):
        if event == "authorization":
            jwt_user_data = parse_jwt_user_data_optional(data["access_token"])

            if jwt_user_data:
                self.user_id = jwt_user_data.user_id

        if not self.user_id:
            raise

        if event == "ping":
            await self.ws.send_json({"event": "pong", data: None})

    async def on_receive(self, text: str):
        message = Message.model_validate_json(text)

        await self.on_event(message.event, message.data)

    async def loop(self):
        try:
            while True:
                text: str = await self.ws.receive_text()

                await self.on_receive(text)
        except Exception:
            await self.manager.disconnect(self)

    async def send_event(self, event: str, data: Any):
        await self.ws.send_json({"event": event, "data": data})


class ConnectionManager:
    def __init__(self):
        self.clients: list[Client] = []

    async def connect(self, websocket: WebSocket):
        client = Client(self, websocket)

        await client.on_connect()

        self.clients.append(client)

        return client

    async def disconnect(self, client: Client):
        try:
            await client.ws.close()
        except Exception:
            pass

        self.clients.remove(client)

    async def broadcast_event(self, event: str, data: Any):
        for client in self.clients:
            await client.send_event(event, data)


manager = ConnectionManager()

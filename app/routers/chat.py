from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        print(f"✅ WebSocket connected: {room}")

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
        print(f"❌ WebSocket disconnected: {room}")

    async def broadcast(self, room: str, message: dict):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/chat/{room}")
async def websocket_chat(websocket: WebSocket, room: str):
    # Принимаем соединение без аутентификации
    await manager.connect(websocket, room)

    # Отправляем приветственное сообщение
    await websocket.send_json(
        {
            "type": "history",
            "user": "System",
            "message": f"Вы подключены к комнате {room}",
            "created_at": "",
        }
    )

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Рассылаем сообщение всем в комнате
            await manager.broadcast(
                room,
                {
                    "type": "message",
                    "user": "User",
                    "message": message_data.get("message", ""),
                    "created_at": "",
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text
import json
from datetime import datetime, timezone
from app.database import async_session_maker
from app.core.logging_config import logger

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[tuple[WebSocket, int, str]]] = {}

    async def connect(self, websocket: WebSocket, room: str, user_id: int, username: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append((websocket, user_id, username))
        logger.info(f"✅ WebSocket connected: user {username} (ID: {user_id}) to room {room}")
        
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to room {room}",
            "user": username
        })

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room] = [
                (ws, uid, name) for ws, uid, name in self.active_connections[room] if ws != websocket
            ]
            if not self.active_connections[room]:
                del self.active_connections[room]
        logger.info(f"❌ WebSocket disconnected from {room}")

    async def broadcast_to_room(self, room: str, message: dict, exclude_user_id: int = None):
        if room not in self.active_connections:
            return
        
        for connection, user_id, username in self.active_connections[room]:
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to user {username}: {e}")


manager = ConnectionManager()


@router.websocket("/ws/chat/{room}")
async def websocket_chat(
    websocket: WebSocket,
    room: str,
):
    # Для разработки - создаем тестового пользователя если нет токена
    # В production нужно использовать реальную аутентификацию
    await websocket.accept()
    
    # Временно используем тестового пользователя для отладки
    test_user_id = 1
    test_username = "TestUser"
    
    logger.info(f"WebSocket connected with test user: {test_username} to room {room}")
    await manager.connect(websocket, room, test_user_id, test_username)
    
    # Загружаем историю сообщений
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                text("""
                    SELECT cm.id, cm.message, cm.created_at, u.username
                    FROM chat_messages cm
                    JOIN "user" u ON u.id = cm.user_id
                    WHERE cm.room = :room
                    ORDER BY cm.created_at DESC
                    LIMIT 50
                """),
                {"room": room}
            )
            rows = result.fetchall()
            
            for row in reversed(rows):
                await websocket.send_json({
                    "type": "history",
                    "user": row.username,
                    "message": row.message,
                    "created_at": row.created_at.isoformat() if row.created_at else "",
                })
        except Exception as e:
            logger.error(f"Error loading history: {e}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_text = message_data.get("message", "").strip()
            
            if not message_text:
                continue
            
            logger.info(f"Received message from {test_username}: {message_text[:50]}")
            
            # Сохраняем сообщение
            async with async_session_maker() as db:
                try:
                    now = datetime.now(timezone.utc)
                    await db.execute(
                        text("""
                            INSERT INTO chat_messages (room, user_id, message, created_at)
                            VALUES (:room, :user_id, :message, :created_at)
                        """),
                        {
                            "room": room,
                            "user_id": test_user_id,
                            "message": message_text,
                            "created_at": now
                        }
                    )
                    await db.commit()
                    
                    broadcast_message = {
                        "type": "message",
                        "user": test_username,
                        "message": message_text,
                        "created_at": now.isoformat(),
                    }
                    
                    await manager.broadcast_to_room(room, broadcast_message)
                    
                except Exception as e:
                    logger.error(f"Error saving message: {e}")
                    await db.rollback()
                    
    except WebSocketDisconnect:
        logger.info(f"User {test_username} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, room)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.models import ChatMessage, User
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatMessage]):
    def __init__(self, session: AsyncSession):
        super().__init__(ChatMessage, session)

    async def get_messages(self, room: str, limit: int = 50) -> List[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.room == room)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def can_access_room(self, user: User, room: str) -> bool:
        """Проверка прав доступа к комнате"""
        if not user:
            return False
        # Все зарегистрированные пользователи могут писать в любые комнаты
        return True


class ChatService:
    def __init__(self, session: AsyncSession):
        self.repo = ChatRepository(session)

    async def save_message(self, room: str, user_id: int, message: str) -> ChatMessage:
        return await self.repo.create(room=room, user_id=user_id, message=message)

    async def get_messages(self, room: str, user: User) -> List[ChatMessage]:
        if not await self.repo.can_access_room(user, room):
            return []
        return await self.repo.get_messages(room)

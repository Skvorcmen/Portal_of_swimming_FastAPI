from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sa_update
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models import RefreshToken
from app.repositories.base import BaseRepository
import secrets


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Репозиторий для работы с refresh токенами"""

    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def create_token(self, user_id: int, expires_days: int = 30) -> RefreshToken:
        """Создать новый refresh token для пользователя"""
        token_value = secrets.token_urlsafe(64)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        token = await self.create(
            token=token_value, user_id=user_id, expires_at=expires_at, revoked=False
        )
        return token

    async def get_by_token(self, token_value: str) -> Optional[RefreshToken]:
        """Найти refresh token по значению"""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token == token_value, RefreshToken.revoked == False
            )
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token_id: int) -> None:
        """Отозвать refresh token"""
        await self.update(token_id, revoked=True)

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """Отозвать все refresh токены пользователя (один запрос)"""
        await self.session.execute(
            sa_update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True)
        )
        await self.session.commit()

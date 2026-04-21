from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models import PasswordResetToken
from app.repositories.base import BaseRepository
import secrets


class PasswordResetRepository(BaseRepository[PasswordResetToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(PasswordResetToken, session)

    async def create_token(self, user_id: int, expires_minutes: int = 60) -> PasswordResetToken:
        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        return await self.create(
            user_id=user_id,
            token=token_value,
            expires_at=expires_at,
            used=False
        )

    async def get_valid_token(self, token: str) -> Optional[PasswordResetToken]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > now
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, token_id: int) -> None:
        await self.update(token_id, used=True)

from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    ExpiredRefreshTokenError,
)
from app.models import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository


class AuthService:
    """Сервис для аутентификации (бизнес-логика)"""

    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role: UserRole,
    ):
        """Зарегистрировать нового пользователя"""
        if await self.user_repo.get_by_email(email):
            raise UserAlreadyExistsError("email", email)

        if await self.user_repo.get_by_username(username):
            raise UserAlreadyExistsError("username", username)

        hashed_password = get_password_hash(password)
        user = await self.user_repo.create(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
        )
        return user

    async def login_user(self, username: str, password: str) -> tuple[str, str]:
        """Возвращает (access_token, refresh_token)"""
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        # Создаём access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )

        # Создаём refresh token
        refresh_token_obj = await self.refresh_token_repo.create_token(user.id)

        return access_token, refresh_token_obj.token

    async def refresh_access_token(self, refresh_token_value: str) -> str:
        """Обновить access token по refresh token"""
        refresh_token = await self.refresh_token_repo.get_by_token(refresh_token_value)
        if not refresh_token:
            raise InvalidRefreshTokenError("Invalid refresh token")

        now = datetime.now(timezone.utc)
        if refresh_token.expires_at < now:  # ← Убрали .replace()
            await self.refresh_token_repo.revoke_token(refresh_token.id)
            raise ExpiredRefreshTokenError("Refresh token expired")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(refresh_token.user_id)},
            expires_delta=access_token_expires,
        )
        return access_token

    async def logout(self, refresh_token_value: str) -> None:
        """Отозвать refresh token"""
        refresh_token = await self.refresh_token_repo.get_by_token(refresh_token_value)
        if refresh_token:
            await self.refresh_token_repo.revoke_token(refresh_token.id)

    async def logout_all_devices(self, user_id: int) -> None:
        """Отозвать все refresh токены пользователя"""
        await self.refresh_token_repo.revoke_all_user_tokens(user_id)

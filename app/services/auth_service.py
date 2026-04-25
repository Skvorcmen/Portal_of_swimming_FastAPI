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
from app.repositories.password_reset_repository import PasswordResetRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)
        self.session = session

    async def register_user(self, email: str, username: str, password: str, full_name: str, role: UserRole):
        if await self.user_repo.get_by_email(email):
            raise UserAlreadyExistsError("email", email)
        if await self.user_repo.get_by_username(username):
            raise UserAlreadyExistsError("username", username)
        hashed_password = get_password_hash(password)
        return await self.user_repo.create(
            email=email, username=username, hashed_password=hashed_password,
            full_name=full_name, role=role
        )

    async def login_user(self, username: str, password: str) -> tuple[str, str]:
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_obj = await self.refresh_token_repo.create_token(user.id)
        return access_token, refresh_token_obj.token

    async def refresh_access_token(self, refresh_token_value: str) -> str:
        refresh_token = await self.refresh_token_repo.get_by_token(refresh_token_value)
        if not refresh_token:
            raise InvalidRefreshTokenError("Invalid refresh token")
        if refresh_token.expires_at < datetime.now(timezone.utc):
            await self.refresh_token_repo.revoke_token(refresh_token.id)
            raise ExpiredRefreshTokenError("Refresh token expired")
        return create_access_token(data={"sub": str(refresh_token.user_id)})

    async def logout(self, refresh_token_value: str) -> None:
        refresh_token = await self.refresh_token_repo.get_by_token(refresh_token_value)
        if refresh_token:
            await self.refresh_token_repo.revoke_token(refresh_token.id)

    async def logout_all_devices(self, user_id: int) -> None:
        await self.refresh_token_repo.revoke_all_user_tokens(user_id)

    async def request_password_reset(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return "reset_token_placeholder"
        repo = PasswordResetRepository(self.session)
        token = await repo.create_token(user.id)
        return token.token

    async def reset_password(self, token: str, new_password: str) -> bool:
        repo = PasswordResetRepository(self.session)
        reset_token = await repo.get_valid_token(token)
        if not reset_token:
            return False
        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            return False
        await self.user_repo.update(user.id, hashed_password=get_password_hash(new_password))
        await repo.mark_as_used(reset_token.id)
        await self.refresh_token_repo.revoke_all_user_tokens(user.id)
        return True

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not verify_password(old_password, user.hashed_password):
            return False
        await self.user_repo.update(user_id, hashed_password=get_password_hash(new_password))
        await self.refresh_token_repo.revoke_all_user_tokens(user_id)
        return True

    async def send_welcome_email(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user and user.email:
            from app.core.email import send_welcome_email
            await send_welcome_email(user.email, user.username)

    async def send_password_reset_email(self, email: str, token: str) -> None:
        from app.core.email import send_password_reset_email
        await send_password_reset_email(email, token)

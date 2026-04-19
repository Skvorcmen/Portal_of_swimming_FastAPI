from datetime import timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.models import User, UserRole
from app.repositories.user_repository import UserRepository


class AuthService:
    """Сервис для аутентификации (бизнес-логика)"""

    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role: UserRole,
    ) -> Tuple[bool, Optional[User], str]:
        """(успех, пользователь или None, текст ошибки)."""
        if await self.user_repo.get_by_email(email):
            return False, None, "Email already registered"

        if await self.user_repo.get_by_username(username):
            return False, None, "Username already taken"

        hashed_password = get_password_hash(password)
        user = await self.user_repo.create(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
        )
        return True, user, ""

    async def login_user(
        self, username: str, password: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Аутентификация пользователя.

        Возвращает:
            (успех, access_token, сообщение_об_ошибке)
        """
        # Ищем пользователя
        user = await self.user_repo.get_by_username(username)
        if not user:
            return False, None, "Incorrect username or password"

        # Проверяем пароль
        if not verify_password(password, user.hashed_password):
            return False, None, "Incorrect username or password"

        # Создаём токен
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        )

        return True, access_token, ""

    async def get_user_by_id(self, user_id: int):
        """Получить пользователя по ID"""
        return await self.user_repo.get_by_id(user_id)

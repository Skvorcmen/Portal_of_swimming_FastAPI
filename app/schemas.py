from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import UserRole


class UserCreate(BaseModel):
    """Схема для регистрации нового пользователя"""

    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole = UserRole.ATHLETE


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя (без пароля)"""

    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема для ответа с токеном"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема для данных внутри токена"""

    user_id: Optional[int] = None

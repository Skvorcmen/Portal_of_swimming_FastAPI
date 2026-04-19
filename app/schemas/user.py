from pydantic import BaseModel, EmailStr, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)




from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Схема для ответа с токеном"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема для данных внутри токена"""
    user_id: Optional[int] = None
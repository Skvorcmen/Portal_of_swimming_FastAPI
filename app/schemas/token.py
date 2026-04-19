from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str


class LogoutRequest(BaseModel):
    refresh_token: str
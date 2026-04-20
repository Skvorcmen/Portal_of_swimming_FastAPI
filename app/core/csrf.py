from secrets import token_urlsafe
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
import hmac


def generate_csrf_token() -> str:
    """Генерирует случайный CSRF токен"""
    return token_urlsafe(32)


def set_csrf_cookie(response: Response, token: str) -> None:
    """Устанавливает CSRF токен в cookie"""
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,  # Должен быть доступен для JavaScript
        secure=False,  # TODO: True в production
        samesite="lax",
        max_age=3600,  # 1 час
    )


def verify_csrf_token(request: Request) -> None:
    """Проверяет CSRF токен из cookie и заголовка"""
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")

    if not cookie_token or not header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token missing"
        )

    # Постоянное время сравнения для защиты от timing attacks
    if not hmac.compare_digest(cookie_token, header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
        )

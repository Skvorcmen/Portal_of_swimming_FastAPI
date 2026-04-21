from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Создаём лимитер
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def setup_rate_limit(app: FastAPI):
    """Настройка rate limiting для приложения"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

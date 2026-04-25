from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.csrf import generate_csrf_token, set_csrf_cookie

class CSRFRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Обновляем CSRF токен при POST/PUT/DELETE запросах
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            new_token = generate_csrf_token()
            set_csrf_cookie(response, new_token)
        
        return response

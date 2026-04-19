from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import auth
from app.core.exceptions import BusinessError

app = FastAPI(
    title="Спортивный портал по плаванию",
    description="Платформа для управления соревнованиями, заплывами и результатами",
    version="1.0.0",
)


# Обработчики исключений
@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Подключаем роутеры API
app.include_router(auth.router)


@app.get("/")
def home():
    return {"message": "Портал по плаванию работает!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

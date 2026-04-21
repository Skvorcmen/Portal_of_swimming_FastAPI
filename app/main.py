from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import auth
from app.core.exceptions import BusinessError
from app.routers import competitions
from app.routers import age_categories
from app.routers import swim_events
from app.routers import entries
from app.routers import heats
from app.routers import chat
from app.routers import news, articles
from app.routers import schools, coaches
from app.routers import coach_profiles
from app.routers import athletes
from app.core.rate_limit import limiter, setup_rate_limit
from app.core.blocklist import is_ip_blocked
from fastapi import Request, HTTPException
from app.core.rate_limit import limiter, setup_rate_limit

app = FastAPI(
    title="Спортивный портал по плаванию",
    description="Платформа для управления соревнованиями, заплывами и результатами",
    version="1.0.0",
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="app/templates")


# Обработчики исключений
@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Подключаем API роутеры
app.include_router(auth.router)

app.include_router(competitions.router)

app.include_router(age_categories.router)

app.include_router(swim_events.router)

app.include_router(entries.router)

app.include_router(heats.router)

app.include_router(chat.router)

app.include_router(news.router)

app.include_router(articles.router)

app.include_router(schools.router)

app.include_router(coaches.router)

app.include_router(coach_profiles.router)

app.include_router(athletes.router)

# После создания app
setup_rate_limit(app)


# После создания app
setup_rate_limit(app)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html")


@app.get("/live")
async def live_page(request: Request):
    """Страница live-таблицы"""
    return templates.TemplateResponse(request=request, name="live.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/test")
async def test_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})


@app.middleware("http")
async def blocklist_middleware(request: Request, call_next):
    ip = request.client.host
    if is_ip_blocked(ip):
        return JSONResponse(
            status_code=429, content={"detail": "IP blocked for 15 minutes"}
        )
    response = await call_next(request)
    return response

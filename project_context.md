# PROJECT CONTEXT DUMP

> Этот файл содержит полный контекст проекта.
> Изучи структуру и все файлы перед выполнением задачи.

---

## 📁 СТРУКТУРА ПРОЕКТА

```
./
├── .pytest_cache/
  ├── README.md
├── README.md
├── alembic.ini
├── app/
  ├── __init__.py
  ├── auth.py
  ├── core/
    ├── __init__.py
    ├── blocklist.py
    ├── cache.py
    ├── config.py
    ├── csrf.py
    ├── dependencies.py
    ├── email.py
    ├── exceptions.py
    ├── logging_config.py
    ├── rate_limit.py
  ├── database.py
  ├── main.py
  ├── models.py
  ├── models_new.py
  ├── repositories/
    ├── __init__.py
    ├── age_category_repository.py
    ├── article_repository.py
    ├── athlete_profile_repository.py
    ├── base.py
    ├── coach_repository.py
    ├── competition_repository.py
    ├── entry_repository.py
    ├── heat_repository.py
    ├── news_repository.py
    ├── password_reset_repository.py
    ├── personal_best_repository.py
    ├── refresh_token_repository.py
    ├── school_repository.py
    ├── swim_event_repository.py
    ├── user_repository.py
  ├── routers/
    ├── __init__.py
    ├── age_categories.py
    ├── articles.py
    ├── athletes.py
    ├── athletes_fix.py
    ├── auth.py
    ├── branches.py
    ├── chat.py
    ├── coach_dashboard.py
    ├── coach_profiles.py
    ├── coaches.py
    ├── competitions.py
    ├── entries.py
    ├── heats.py
    ├── news.py
    ├── schools.py
    ├── swim_events.py
  ├── schemas/
    ├── __init__.py
    ├── token.py
    ├── user.py
  ├── services/
    ├── __init__.py
    ├── age_category_service.py
    ├── article_service.py
    ├── athlete_service.py
    ├── auth_service.py
    ├── chat_service.py
    ├── coach_service.py
    ├── competition_service.py
    ├── csv_service.py
    ├── entry_service.py
    ├── heat_service.py
    ├── image_service.py
    ├── news_service.py
    ├── pdf_service.py
    ├── school_service.py
    ├── swim_event_service.py
  ├── static/
    ├── css/
      ├── style.css
    ├── js/
      ├── auth.js
      ├── toast.js
  ├── templates/
    ├── athlete_detail.html
    ├── base.html
    ├── branch_detail.html
    ├── coach_dashboard.html
    ├── coach_detail.html
    ├── coach_student_detail.html
    ├── competition_detail.html
    ├── competitions_list.html
    ├── emails/
      ├── password_reset.html
      ├── welcome.html
    ├── index.html
    ├── live.html
    ├── login.html
    ├── news_detail.html
    ├── news_list.html
    ├── partials/
      ├── article_items.html
      ├── chat.html
      ├── competition_items.html
      ├── confirm_modal.html
      ├── news_items.html
      ├── school_items.html
    ├── profile.html
    ├── register.html
    ├── school_detail.html
    ├── schools_list.html
    ├── test.html
├── docker-compose.yml
├── docs/
  ├── pages/
    ├── athlete-detail.md
    ├── coach-detail.md
    ├── competition-detail.md
    ├── competitions-list.md
    ├── live.md
    ├── news-list.md
    ├── profile.md
    ├── register.md
    ├── school-detail.md
    ├── schools-list.md
├── init_production_db.py
├── requirements.txt
```

---

## 📄 СОДЕРЖИМОЕ ФАЙЛОВ

### `.pytest_cache/README.md`

```markdown
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.
```

---

### `README.md`

```markdown
# Portal_of_swimming_FastAPI
```

---

### `alembic.ini`

```ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://postgres:secretpassword@localhost:5432/swimming
[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 88

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

### `app/auth.py`

```python
from jose import JWTError, jwt
from app.core.config import settings

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.core.config import settings
from app.repositories.user_repository import UserRepository

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if "sub" in to_encode and isinstance(to_encode["sub"], int):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def _get_user_by_token(token: str, db: AsyncSession) -> User:
    """Общая логика получения пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Получает пользователя из Bearer токена (для Swagger)"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_user_by_token(token, db)


async def get_current_user_from_cookie(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Получает пользователя из HttpOnly cookie (для браузера)"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_user_by_token(token, db)


async def get_current_user_optional_cookie(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """Поддерживает оба способа: cookie ИЛИ Bearer токен"""
    raw_token = request.cookies.get("access_token") or token
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_user_by_token(raw_token, db)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_from_websocket(
    websocket, db: AsyncSession
):
    """Получает пользователя из cookie для WebSocket соединения"""
    token = websocket.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            return None
    except (JWTError, TypeError, ValueError):
        return None

    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    return user


async def get_current_user_from_cookie(request: Request, db: AsyncSession) -> Optional[User]:
    """Получает пользователя из HttpOnly cookie (для ручного использования)"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        return await _get_user_by_token(token, db)
    except HTTPException:
        return None
```

---

### `app/core/blocklist.py`

```python
from datetime import datetime, timedelta
from collections import defaultdict

# Хранилище заблокированных IP (в продакшене использовать Redis)
blocked_ips = {}
failed_attempts = defaultdict(int)


def is_ip_blocked(ip: str) -> bool:
    """Проверка, заблокирован ли IP"""
    if ip in blocked_ips:
        if blocked_ips[ip] > datetime.now():
            return True
        else:
            del blocked_ips[ip]
    return False


def record_failed_attempt(ip: str) -> bool:
    """Запись неудачной попытки. Возвращает True если IP заблокирован"""
    failed_attempts[ip] += 1
    
    if failed_attempts[ip] >= 10:
        blocked_ips[ip] = datetime.now() + timedelta(minutes=15)
        return True
    return False


def reset_attempts(ip: str) -> None:
    """Сброс счётчика попыток"""
    if ip in failed_attempts:
        del failed_attempts[ip]
```

---

### `app/core/cache.py`

```python
import redis.asyncio as redis
import json
from typing import Optional, Any
from functools import wraps

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    return redis_client


async def set_cache(key: str, value: Any, expire: int = 300) -> None:
    r = await get_redis()
    await r.setex(key, expire, json.dumps(value, default=str))


async def get_cache(key: str) -> Optional[Any]:
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None


async def delete_cache(key: str) -> None:
    r = await get_redis()
    await r.delete(key)


async def clear_cache_pattern(pattern: str) -> None:
    r = await get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)


def cached(expire: int = 300, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Исключаем service из ключа кэша (все Depends объекты)
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != "service"}
            
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(sorted(filtered_kwargs.items()))}"
            
            cached_data = await get_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, expire)
            return result
        return wrapper
    return decorator
```

---

### `app/core/config.py`

```python
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Все настройки приложения в одном месте"""

    # База данных
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Refresh token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Приложение
    DEBUG: bool = False

    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Создаём один экземпляр настроек для всего приложения
settings = Settings()
```

---

### `app/core/csrf.py`

```python
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
```

---

### `app/core/dependencies.py`

```python
from fastapi import Depends, HTTPException, status

from app.auth import get_current_user
from app.models import User, UserRole


def require_role(required_roles: list[UserRole]):
    """Dependency factory: доступ только для перечисленных ролей (+ ADMIN всегда)."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        allowed = set(required_roles) | {UserRole.ADMIN}
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not allowed. Required: {required_roles}",
            )
        return current_user

    return role_checker
```

---

### `app/core/email.py`

```python
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import settings
from app.core.logging_config import logger

template_dir = Path(__file__).parent.parent / "templates" / "emails"
template_env = Environment(loader=FileSystemLoader(template_dir))


async def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: dict,
) -> bool:
    try:
        template = template_env.get_template(template_name)
        html_content = template.render(**context)
        
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(html_content, subtype="html")
        
        # Подключаемся без SSL, затем включаем STARTTLS
        smtp = SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
        await smtp.connect()
        await smtp.starttls()  # Включаем шифрование
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
        
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False


async def send_welcome_email(to_email: str, username: str):
    return await send_email(
        to_email=to_email,
        subject="Добро пожаловать в Плавательный портал!",
        template_name="welcome.html",
        context={"username": username}
    )


async def send_password_reset_email(to_email: str, token: str):
    reset_link = f"http://localhost:8000/auth/reset-password-page?token={token}"
    return await send_email(
        to_email=to_email,
        subject="Сброс пароля",
        template_name="password_reset.html",
        context={"reset_link": reset_link, "token": token}
    )
```

---

### `app/core/exceptions.py`

```python
"""Кастомные исключения для бизнес-логики"""


class BusinessError(Exception):
    """Базовое исключение для бизнес-ошибок"""

    pass


class UserAlreadyExistsError(BusinessError):
    """Пользователь с таким email или username уже существует"""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"{field} already registered: {value}")


class InvalidCredentialsError(BusinessError):
    """Неверный username или пароль"""

    pass


class UserNotFoundError(BusinessError):
    """Пользователь не найден"""

    pass


class InvalidRefreshTokenError(BusinessError):
    """Невалидный refresh token"""

    pass


class ExpiredRefreshTokenError(BusinessError):
    """Истёкший refresh token"""

    pass


class FileTooLargeError(BusinessError):
    """Файл слишком большой"""

    pass


class InvalidFileError(BusinessError):
    """Невалидный файл"""

    pass
```

---

### `app/core/logging_config.py`

```python
import logging
import sys

def setup_logging():
    """Настройка логирования для всего приложения"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )
    
    # Устанавливаем уровень для сторонних библиотек
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()
```

---

### `app/core/rate_limit.py`

```python
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
```

---

### `app/database.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,  # Максимум соединений в пуле
    max_overflow=10,  # Дополнительные соединения при пиковой нагрузке
    pool_pre_ping=True,  # Проверять соединение перед использованием
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_maker() as session:
        yield session
```

---

### `app/main.py`

```python
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import auth
from app.routers import branches
from app.core.exceptions import BusinessError
from app.routers import competitions
from app.routers import branches
from app.routers import age_categories
from app.routers import branches
from app.routers import swim_events
from app.routers import branches
from app.routers import entries
from app.routers import branches
from app.routers import heats
from app.routers import branches
from app.routers import chat
from app.routers import branches
from app.routers import news, articles
from app.routers import branches
from app.routers import schools, coaches
from app.routers import branches
from app.routers import coach_profiles
from app.routers import branches
from app.routers import athletes
from app.routers import branches
from app.routers import coach_dashboard
from app.routers import branches
from app.core.rate_limit import setup_rate_limit
from app.core.blocklist import is_ip_blocked
from app.models import User
from app.auth import get_current_user_optional_cookie
from fastapi import HTTPException

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
app.include_router(branches.router)
app.include_router(news.router)
app.include_router(articles.router)
app.include_router(schools.router)
app.include_router(coaches.router)
app.include_router(coach_profiles.router)
app.include_router(athletes.router)
app.include_router(coach_dashboard.router)

# Настройка rate limiting (ОДИН РАЗ)
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


@app.on_event("startup")
async def startup():
    from app.core.cache import get_redis

    try:
        r = await get_redis()
        await r.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

# Обновляем страницу профиля - передаем current_user в шаблон


@app.get("/profile")
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional_cookie)
):
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "current_user": current_user}
    )
```

---

### `app/models.py`

```python
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class UserRole(enum.Enum):
    GUEST = "guest"
    ATHLETE = "athlete"
    COACH = "coach"
    SCHOOL_REP = "school_rep"
    SECRETARY = "secretary"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.GUEST)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    athlete_profile: Mapped[Optional["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="user", uselist=False
    )
    coach_profile: Mapped[Optional["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="user", uselist=False
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(
        String(500), unique=True, nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)

    # НОВЫЕ ПОЛЯ
    founder: Mapped[str] = mapped_column(String(200), nullable=True)  # Основатель
    founded_year: Mapped[int] = mapped_column(Integer, nullable=True)  # Год основания
    city: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)  # Нынешний адрес
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    website: Mapped[str] = mapped_column(String(200), nullable=True)

    # ИЗОБРАЖЕНИЯ
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)  # Логотип
    cover_url: Mapped[str] = mapped_column(String(500), nullable=True)  # Обложка школы

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    branches: Mapped[list["Branch"]] = relationship(
        "Branch", back_populates="school", cascade="all, delete-orphan"
    )
    athletes: Mapped[list["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="school"
    )
    coaches: Mapped[list["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="school"
    )


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    # НОВОЕ ПОЛЕ - обложка филиала (если нет - берется от школы)
    cover_url: Mapped[str] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    school: Mapped["School"] = relationship("School", back_populates="branches")
    athletes: Mapped[list["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="branch"
    )
    coaches: Mapped[list["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="branch"
    )


class CoachProfile(Base):
    __tablename__ = "coach_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ИЗОБРАЖЕНИЯ
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)  # Аватар тренера
    cover_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Обложка (берется от школы если не указана)

    bio: Mapped[str] = mapped_column(String(1000), nullable=True)
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    qualification: Mapped[str] = mapped_column(String(100), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    specialization: Mapped[str] = mapped_column(String(200), nullable=True)
    is_head_coach: Mapped[bool] = mapped_column(Boolean, default=False)
    achievements: Mapped[str] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="coach_profile")
    school: Mapped[Optional["School"]] = relationship(
        "School", back_populates="coaches"
    )
    branch: Mapped[Optional["Branch"]] = relationship(
        "Branch", back_populates="coaches"
    )
    athletes: Mapped[list["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="coach"
    )


class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("coach_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ИЗОБРАЖЕНИЯ
    photo_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Аватар спортсмена
    cover_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Обложка (берется от школы если не указана)

    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True, index=True)
    rank: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="athlete_profile")
    school: Mapped[Optional["School"]] = relationship(
        "School", back_populates="athletes"
    )
    branch: Mapped[Optional["Branch"]] = relationship(
        "Branch", back_populates="athletes"
    )
    coach: Mapped[Optional["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="athletes"
    )
    personal_bests: Mapped[list["PersonalBest"]] = relationship(
        "PersonalBest", back_populates="athlete", cascade="all, delete-orphan"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="athlete", cascade="all, delete-orphan"
    )


class PersonalBest(Base):
    __tablename__ = "personal_bests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    athlete_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("athlete_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    distance: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 50, 100, 200, 400, 800, 1500
    stroke: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # freestyle, breaststroke, backstroke, butterfly
    time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    set_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    athlete: Mapped["AthleteProfile"] = relationship(
        "AthleteProfile", back_populates="personal_bests"
    )


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[str] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    max_participants: Mapped[int] = mapped_column(Integer, default=0)

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи (пока закомментируем, добавим позже)
    age_categories: Mapped[list["AgeCategory"]] = relationship(
        "AgeCategory", back_populates="competition", cascade="all, delete-orphan"
    )
    swim_events: Mapped[list["SwimEvent"]] = relationship(
        "SwimEvent", back_populates="competition", cascade="all, delete-orphan"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="competition", cascade="all, delete-orphan"
    )
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])


class AgeCategory(Base):
    __tablename__ = "age_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "10-12 лет", "13-15 лет"
    min_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(
        String(10), nullable=True
    )  # male, female, mixed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связь с соревнованием
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="age_categories"
    )


class SwimEvent(Base):
    __tablename__ = "swim_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # "50m Freestyle"
    distance: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 50, 100, 200, 400, 800, 1500
    stroke: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # freestyle, breaststroke, backstroke, butterfly, medley
    gender: Mapped[str] = mapped_column(
        String(10), nullable=True
    )  # male, female, mixed
    is_relay: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)  # порядок проведения
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="swim_events"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="swim_event", cascade="all, delete-orphan"
    )
    heats: Mapped[list["Heat"]] = relationship(
        "Heat", back_populates="swim_event", cascade="all, delete-orphan"
    )


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    swim_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("swim_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    athlete_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("athlete_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, confirmed, rejected, scratched
    entry_time: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # заявленное время (сек)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="entries"
    )
    swim_event: Mapped["SwimEvent"] = relationship(
        "SwimEvent", back_populates="entries"
    )
    athlete: Mapped["AthleteProfile"] = relationship(
        "AthleteProfile", back_populates="entries"
    )
    heat_entry: Mapped[Optional["HeatEntry"]] = relationship(
        "HeatEntry", back_populates="entry", uselist=False
    )


class Heat(Base):
    __tablename__ = "heats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    swim_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("swim_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    heat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lane_count: Mapped[int] = mapped_column(Integer, default=8)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    swim_event: Mapped["SwimEvent"] = relationship("SwimEvent", back_populates="heats")
    entries: Mapped[list["HeatEntry"]] = relationship(
        "HeatEntry", back_populates="heat", cascade="all, delete-orphan"
    )


class HeatEntry(Base):
    __tablename__ = "heat_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    heat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("heats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    lane: Mapped[int] = mapped_column(Integer, nullable=False)
    result_time: Mapped[float] = mapped_column(Float, nullable=True)
    place: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    heat: Mapped["Heat"] = relationship("Heat", back_populates="entries")
    entry: Mapped["Entry"] = relationship("Entry", back_populates="heat_entry")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # competition_1 или support
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", backref="chat_messages")


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    author: Mapped[Optional["User"]] = relationship("User", backref="news")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(10000), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # technique, nutrition, rules, etc.
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    author: Mapped[Optional["User"]] = relationship("User", backref="articles")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", backref="password_reset_tokens")
```

---

### `app/models_new.py`

```python
# ДОБАВЬТЕ ЭТИ ПОЛЯ В СУЩЕСТВУЮЩИЕ МОДЕЛИ:

# В класс School добавьте:
# founder: Mapped[str] = mapped_column(String(200), nullable=True)
# founded_year: Mapped[int] = mapped_column(Integer, nullable=True)

# В класс CoachProfile добавьте:
# cover_url: Mapped[str] = mapped_column(String(500), nullable=True)

# В класс AthleteProfile добавьте:
# cover_url: Mapped[str] = mapped_column(String(500), nullable=True)
```

---

### `app/repositories/age_category_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models import AgeCategory
from app.repositories.base import BaseRepository


class AgeCategoryRepository(BaseRepository[AgeCategory]):
    """Репозиторий для работы с возрастными категориями"""

    def __init__(self, session: AsyncSession):
        super().__init__(AgeCategory, session)

    async def get_by_competition(self, competition_id: int) -> List[AgeCategory]:
        """Получить все возрастные категории для соревнования"""
        result = await self.session.execute(
            select(AgeCategory)
            .where(AgeCategory.competition_id == competition_id)
            .order_by(AgeCategory.min_age)
        )
        return result.scalars().all()

    async def get_by_competition_and_gender(
        self, competition_id: int, gender: str
    ) -> List[AgeCategory]:
        """Получить возрастные категории для соревнования по полу"""
        result = await self.session.execute(
            select(AgeCategory)
            .where(AgeCategory.competition_id == competition_id)
            .where(AgeCategory.gender == gender)
            .order_by(AgeCategory.min_age)
        )
        return result.scalars().all()
```

---

### `app/repositories/article_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from app.models import Article
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    def __init__(self, session: AsyncSession):
        super().__init__(Article, session)

    async def get_published(self, skip: int = 0, limit: int = 100) -> List[Article]:
        result = await self.session.execute(
            select(Article)
            .where(Article.is_published == True)
            .order_by(desc(Article.published_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        result = await self.session.execute(
            select(Article)
            .where(Article.is_published == True, Article.category == category)
            .order_by(desc(Article.published_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def increment_views(self, article_id: int) -> None:
        article = await self.get_by_id(article_id)
        if article:
            await self.update(article_id, views=article.views + 1)

    async def search(
        self, query: str = "", category: str = "", page: int = 1, limit: int = 10
    ) -> dict:
        stmt = select(Article).where(Article.is_published == True)

        if query:
            stmt = stmt.where(
                (Article.title.ilike(f"%{query}%"))
                | (Article.content.ilike(f"%{query}%"))
            )
        if category:
            stmt = stmt.where(Article.category == category)

        stmt = stmt.order_by(desc(Article.published_at))

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = (
            select(func.count())
            .select_from(Article)
            .where(Article.is_published == True)
        )
        if query:
            count_stmt = count_stmt.where(
                (Article.title.ilike(f"%{query}%"))
                | (Article.content.ilike(f"%{query}%"))
            )
        if category:
            count_stmt = count_stmt.where(Article.category == category)
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
```

---

### `app/repositories/athlete_profile_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import AthleteProfile, CoachProfile
from app.repositories.base import BaseRepository


class AthleteProfileRepository(BaseRepository[AthleteProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(AthleteProfile, session)

    async def get_by_school(self, school_id: int) -> List[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile).where(AthleteProfile.school_id == school_id)
        )
        return result.scalars().all()

    async def get_by_coach(self, coach_id: int) -> List[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile).where(AthleteProfile.coach_id == coach_id)
        )
        return result.scalars().all()

    async def get_by_user_id(self, user_id: int) -> Optional[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile).where(AthleteProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, athlete_id: int) -> Optional[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile)
            .options(
                selectinload(AthleteProfile.user),
                selectinload(AthleteProfile.school),
                selectinload(AthleteProfile.coach).selectinload(CoachProfile.user),
                selectinload(AthleteProfile.personal_bests)
            )
            .where(AthleteProfile.id == athlete_id)
        )
        return result.scalar_one_or_none()
```

---

### `app/repositories/base.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import TypeVar, Generic, Type, Optional, List
from app.database import Base

# Тип для модели SQLAlchemy
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с CRUD операциями.
    Все другие репозитории будут наследоваться от него.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """Создать одну запись"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Найти запись по ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить все записи с пагинацией"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись по ID"""
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """Удалить запись по ID"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
```

---

### `app/repositories/coach_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import CoachProfile, User
from app.repositories.base import BaseRepository


class CoachRepository(BaseRepository[CoachProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(CoachProfile, session)

    async def get_by_school(self, school_id: int) -> List[CoachProfile]:
        result = await self.session.execute(
            select(CoachProfile)
            .options(selectinload(CoachProfile.user))
            .where(CoachProfile.school_id == school_id)
        )
        return result.scalars().all()

    async def get_by_id(self, coach_id: int) -> Optional[CoachProfile]:
        result = await self.session.execute(
            select(CoachProfile)
            .options(selectinload(CoachProfile.user))
            .where(CoachProfile.id == coach_id)
        )
        return result.scalar_one_or_none()

    async def search(self, name: str = "", school_id: int = None) -> List[CoachProfile]:
        stmt = select(CoachProfile).options(selectinload(CoachProfile.user))
        
        if name:
            stmt = stmt.join(User).where(User.full_name.ilike(f"%{name}%"))
        if school_id:
            stmt = stmt.where(CoachProfile.school_id == school_id)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

---

### `app/repositories/competition_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from app.models import Competition
from app.repositories.base import BaseRepository
from sqlalchemy import select, desc, func, and_


class CompetitionRepository(BaseRepository[Competition]):
    """Репозиторий для работы с соревнованиями"""

    def __init__(self, session: AsyncSession):
        super().__init__(Competition, session)

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[Competition]:
        """Найти соревнования по статусу"""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active(self, skip: int = 0, limit: int = 100) -> List[Competition]:
        result = await self.session.execute(
            select(Competition)
            .where(
                Competition.status.in_(
                    [
                        "registration_open",
                        "registration_closed",
                        "ongoing",
                    ]
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_upcoming(self, skip: int = 0, limit: int = 100) -> List[Competition]:
        """Найти предстоящие соревнования"""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(Competition)
            .where(Competition.start_date > now)
            .where(Competition.status != "cancelled")
            .order_by(Competition.start_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search(
        self,
        name: str = "",
        city: str = "",
        status: str = "",
        page: int = 1,
        limit: int = 10,
    ) -> dict:
        from sqlalchemy import func, and_, desc

        stmt = select(Competition)
        filters = []
        if name:
            filters.append(Competition.name.ilike(f"%{name}%"))
        if city:
            filters.append(Competition.city.ilike(f"%{city}%"))
        if status:
            filters.append(Competition.status == status)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(desc(Competition.start_date))

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(Competition)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
```

---

### `app/repositories/entry_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from app.models import Entry
from app.repositories.base import BaseRepository


class EntryRepository(BaseRepository[Entry]):
    """Репозиторий для работы с заявками"""

    def __init__(self, session: AsyncSession):
        super().__init__(Entry, session)

    async def get_by_competition(self, competition_id: int) -> List[Entry]:
        """Получить все заявки для соревнования"""
        result = await self.session.execute(
            select(Entry)
            .where(Entry.competition_id == competition_id)
            .order_by(Entry.created_at)
        )
        return result.scalars().all()

    async def get_by_swim_event(self, swim_event_id: int) -> List[Entry]:
        """Получить все заявки для дистанции"""
        result = await self.session.execute(
            select(Entry)
            .where(Entry.swim_event_id == swim_event_id)
            .order_by(Entry.entry_time)
        )
        return result.scalars().all()

    async def get_by_athlete(self, athlete_id: int) -> List[Entry]:
        """Получить все заявки спортсмена"""
        result = await self.session.execute(
            select(Entry)
            .where(Entry.athlete_id == athlete_id)
            .order_by(Entry.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_status(self, status: str) -> List[Entry]:
        """Получить заявки по статусу"""
        result = await self.session.execute(select(Entry).where(Entry.status == status))
        return result.scalars().all()

    async def update_status(self, entry_id: int, status: str) -> Optional[Entry]:
        """Обновить статус заявки"""
        return await self.update(entry_id, status=status)
```

---

### `app/repositories/heat_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from app.models import Heat, HeatEntry
from app.repositories.base import BaseRepository


class HeatRepository(BaseRepository[Heat]):
    def __init__(self, session: AsyncSession):
        super().__init__(Heat, session)

    async def get_by_swim_event(self, swim_event_id: int) -> List[Heat]:
        result = await self.session.execute(
            select(Heat)
            .where(Heat.swim_event_id == swim_event_id)
            .order_by(Heat.heat_number)
        )
        return result.scalars().all()


class HeatEntryRepository(BaseRepository[HeatEntry]):
    def __init__(self, session: AsyncSession):
        super().__init__(HeatEntry, session)

    async def get_by_heat(self, heat_id: int) -> List[HeatEntry]:
        result = await self.session.execute(
            select(HeatEntry)
            .where(HeatEntry.heat_id == heat_id)
            .order_by(HeatEntry.lane)
        )
        return result.scalars().all()

    async def update_result(self, heat_entry_id: int, result_time: float) -> HeatEntry:
        """Обновить результат участника"""
        return await self.update(heat_entry_id, result_time=result_time)
```

---

### `app/repositories/news_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models import News
from app.repositories.base import BaseRepository
from sqlalchemy import select, desc, func


class NewsRepository(BaseRepository[News]):
    def __init__(self, session: AsyncSession):
        super().__init__(News, session)

    async def get_published(self, skip: int = 0, limit: int = 100) -> List[News]:
        result = await self.session.execute(
            select(News)
            .where(News.is_published == True)
            .order_by(desc(News.published_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_author(self, author_id: int) -> List[News]:
        result = await self.session.execute(
            select(News)
            .where(News.author_id == author_id)
            .order_by(desc(News.created_at))
        )
        return result.scalars().all()

    from sqlalchemy import func, desc

    async def search(
        self, query: str = "", sort: str = "newest", page: int = 1, limit: int = 10
    ) -> dict:
        stmt = select(News).where(News.is_published == True)

        if query:
            stmt = stmt.where(
                (News.title.ilike(f"%{query}%")) | (News.content.ilike(f"%{query}%"))
            )

        if sort == "newest":
            stmt = stmt.order_by(desc(News.published_at))
        else:
            stmt = stmt.order_by(News.published_at)

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = (
            select(func.count()).select_from(News).where(News.is_published == True)
        )
        if query:
            count_stmt = count_stmt.where(
                (News.title.ilike(f"%{query}%")) | (News.content.ilike(f"%{query}%"))
            )
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
```

---

### `app/repositories/password_reset_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models import PasswordResetToken
from app.repositories.base import BaseRepository
import secrets


class PasswordResetRepository(BaseRepository[PasswordResetToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(PasswordResetToken, session)

    async def create_token(self, user_id: int, expires_minutes: int = 60) -> PasswordResetToken:
        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        return await self.create(
            user_id=user_id,
            token=token_value,
            expires_at=expires_at,
            used=False
        )

    async def get_valid_token(self, token: str) -> Optional[PasswordResetToken]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > now
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, token_id: int) -> None:
        await self.update(token_id, used=True)
```

---

### `app/repositories/personal_best_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models import PersonalBest
from app.repositories.base import BaseRepository


class PersonalBestRepository(BaseRepository[PersonalBest]):
    def __init__(self, session: AsyncSession):
        super().__init__(PersonalBest, session)

    async def get_by_athlete(self, athlete_id: int) -> List[PersonalBest]:
        """Получить все рекорды спортсмена"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.athlete_id == athlete_id)
            .order_by(self.model.distance, self.model.time_seconds)
        )
        return result.scalars().all()


    async def get_by_id(self, pb_id: int):
        """Получить рекорд по ID"""
        from sqlalchemy import select
        result = await self.session.execute(
            select(self.model).where(self.model.id == pb_id)
        )
        return result.scalar_one_or_none()
```

---

### `app/repositories/refresh_token_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sa_update
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models import RefreshToken
from app.repositories.base import BaseRepository
import secrets


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Репозиторий для работы с refresh токенами"""

    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def create_token(self, user_id: int, expires_days: int = 30) -> RefreshToken:
        """Создать новый refresh token для пользователя"""
        token_value = secrets.token_urlsafe(64)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        token = await self.create(
            token=token_value, user_id=user_id, expires_at=expires_at, revoked=False
        )
        return token

    async def get_by_token(self, token_value: str) -> Optional[RefreshToken]:
        """Найти refresh token по значению"""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token == token_value, RefreshToken.revoked == False
            )
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token_id: int) -> None:
        """Отозвать refresh token"""
        await self.update(token_id, revoked=True)

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """Отозвать все refresh токены пользователя (один запрос)"""
        await self.session.execute(
            sa_update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True)
        )
        await self.session.commit()
```

---

### `app/repositories/school_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc
from typing import Optional, List
from app.models import School
from app.repositories.base import BaseRepository


class SchoolRepository(BaseRepository[School]):
    def __init__(self, session: AsyncSession):
        super().__init__(School, session)

    async def get_by_city(self, city: str) -> List[School]:
        result = await self.session.execute(select(School).where(School.city == city))
        return result.scalars().all()

    async def search(
        self, name: str = "", city: str = "", page: int = 1, limit: int = 10
    ) -> dict:
        stmt = select(School)
        filters = []

        if name:
            filters.append(School.name.ilike(f"%{name}%"))
        if city:
            filters.append(School.city.ilike(f"%{city}%"))

        if filters:
            stmt = stmt.where(or_(*filters))

        stmt = stmt.order_by(School.name)

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(School)
        if filters:
            count_stmt = count_stmt.where(or_(*filters))
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
```

---

### `app/repositories/swim_event_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models import SwimEvent
from app.repositories.base import BaseRepository


class SwimEventRepository(BaseRepository[SwimEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(SwimEvent, session)

    async def get_by_competition(self, competition_id: int) -> List[SwimEvent]:
        result = await self.session.execute(
            select(SwimEvent)
            .where(SwimEvent.competition_id == competition_id)
            .order_by(SwimEvent.order, SwimEvent.distance)
        )
        return result.scalars().all()
```

---

### `app/repositories/user_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Найти пользователя по email"""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Найти пользователя по username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_role(
        self, role: UserRole, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Найти всех пользователей с определённой ролью"""
        result = await self.session.execute(
            select(User).where(User.role == role).offset(skip).limit(limit)
        )
        return result.scalars().all()
```

---

### `app/routers/age_categories.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.age_category_service import AgeCategoryService
from app.auth import get_current_active_user
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/age-categories", tags=["age-categories"])


def get_age_category_service(db: AsyncSession = Depends(get_db)) -> AgeCategoryService:
    return AgeCategoryService(db)


# Схемы
class AgeCategoryCreate(BaseModel):
    competition_id: int
    name: str
    min_age: int
    max_age: int
    gender: str | None = None


class AgeCategoryUpdate(BaseModel):
    name: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    gender: str | None = None


class AgeCategoryResponse(BaseModel):
    id: int
    competition_id: int
    name: str
    min_age: int
    max_age: int
    gender: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=AgeCategoryResponse)
async def create_age_category(
    category_data: AgeCategoryCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Создать возрастную категорию (ADMIN, SECRETARY)"""
    if category_data.min_age >= category_data.max_age:
        raise HTTPException(status_code=400, detail="min_age must be less than max_age")

    category = await service.create_age_category(
        competition_id=category_data.competition_id,
        name=category_data.name,
        min_age=category_data.min_age,
        max_age=category_data.max_age,
        gender=category_data.gender,
    )
    return category


@router.get("/competition/{competition_id}", response_model=List[AgeCategoryResponse])
async def get_categories_by_competition(
    competition_id: int,
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Получить все возрастные категории для соревнования"""
    return await service.get_categories_by_competition(competition_id)


@router.get("/{category_id}", response_model=AgeCategoryResponse)
async def get_age_category(
    category_id: int,
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Получить возрастную категорию по ID"""
    category = await service.get_age_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Age category not found")
    return category


@router.put("/{category_id}", response_model=AgeCategoryResponse)
async def update_age_category(
    category_id: int,
    category_data: AgeCategoryUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Обновить возрастную категорию (ADMIN, SECRETARY)"""
    update_data = {k: v for k, v in category_data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    category = await service.update_age_category(category_id, **update_data)
    if not category:
        raise HTTPException(status_code=404, detail="Age category not found")
    return category


@router.delete("/{category_id}")
async def delete_age_category(
    category_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Удалить возрастную категорию (ADMIN, SECRETARY)"""
    deleted = await service.delete_age_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Age category not found")
    return {"message": "Age category deleted successfully"}
```

---

### `app/routers/articles.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.article_service import ArticleService
from app.models import User, UserRole
from app.core.dependencies import require_role
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/articles", tags=["articles"])


def get_article_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


class ArticleCreate(BaseModel):
    title: str
    content: str
    category: str
    summary: str | None = None


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    summary: str | None = None


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    category: str
    author_id: int | None
    views: int
    is_published: bool
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ArticleResponse)
async def create_article(
    data: ArticleCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    return await service.create_article(
        title=data.title,
        content=data.content,
        category=data.category,
        summary=data.summary,
        author_id=current_user.id,
    )


@router.post("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    article = await service.publish_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/", response_model=List[ArticleResponse])
async def get_all_articles(
    skip: int = 0,
    limit: int = 100,
    service: ArticleService = Depends(get_article_service),
):
    return await service.get_all_published(skip, limit)


@router.get("/category/{category}", response_model=List[ArticleResponse])
async def get_articles_by_category(
    category: str,
    service: ArticleService = Depends(get_article_service),
):
    return await service.get_by_category(category)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
):
    article = await service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Увеличиваем счётчик просмотров
    await service.increment_views(article_id)
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    article = await service.update_article(article_id, **update_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    deleted = await service.delete_article(article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}


@router.get("/page")
async def articles_page(request: Request):
    return templates.TemplateResponse("articles_list.html", {"request": request})


@router.get("/search")
async def search_articles(
    request: Request,
    q: str = "",
    category: str = "",
    page: int = 1,
    service: ArticleService = Depends(get_article_service),
):
    result = await service.search_articles(q, category, page)
    return templates.TemplateResponse(
        "partials/article_items.html",
        {
            "request": request,
            "articles": result["items"],
            "page": page,
            "total": result["total"],
            "pages": result["pages"],
        },
    )
```

---

### `app/routers/athletes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.athlete_service import AthleteService
from app.services.school_service import SchoolService
from app.services.coach_service import CoachService
from app.models import User, UserRole
from app.core.dependencies import require_role
from app.auth import get_current_user_optional_cookie, get_current_active_user

router = APIRouter(prefix="/athletes", tags=["athletes"])
templates = Jinja2Templates(directory="app/templates")


def get_athlete_service(db: AsyncSession = Depends(get_db)) -> AthleteService:
    return AthleteService(db)


def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)


# ===== ЛИЧНЫЕ РЕКОРДЫ =====

class PersonalBestCreate(BaseModel):
    distance: int
    stroke: str
    time_seconds: float


class PersonalBestResponse(BaseModel):
    id: int
    athlete_id: int
    distance: int
    stroke: str
    time_seconds: float
    set_at: datetime

    class Config:
        from_attributes = True


# ===== ЭНДПОИНТЫ ДЛЯ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ =====
# Используем get_current_user_optional_cookie для поддержки cookie

@router.get("/my/personal-bests")
async def get_my_personal_bests(
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    """Получить личные рекорды текущего пользователя-спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated or not athlete")
    
    athlete = await service.get_athlete_by_user_id(current_user.id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    
    pbs = await service.get_personal_bests(athlete.id)
    return pbs


@router.post("/my/personal-bests", response_model=PersonalBestResponse)
async def add_my_personal_best(
    data: PersonalBestCreate,
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    """Добавить личный рекорд для текущего пользователя-спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated or not athlete")
    
    athlete = await service.get_athlete_by_user_id(current_user.id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    
    pb = await service.add_personal_best(
        athlete_id=athlete.id,
        distance=data.distance,
        stroke=data.stroke,
        time_seconds=data.time_seconds,
    )
    return pb


@router.get("/my/profile")
async def my_profile(
    request: Request,
    current_user: User = Depends(get_current_user_optional_cookie),
    athlete_service: AthleteService = Depends(get_athlete_service),
):
    """Страница "Мои рекорды" для авторизованного спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    athlete = await athlete_service.get_athlete_by_user_id(current_user.id)
    if not athlete:
        return templates.TemplateResponse(
            "athlete_no_profile.html", {"request": request}
        )
    
    return templates.TemplateResponse(
        "athlete_my_profile.html", {"request": request, "athlete": athlete}
    )


# ===== ЭНДПОИНТЫ ДЛЯ ПРОСМОТРА ДРУГИХ СПОРТСМЕНОВ =====

@router.get("/{athlete_id}/page")
async def athlete_detail_page(
    athlete_id: int,
    request: Request,
    athlete_service: AthleteService = Depends(get_athlete_service),
    school_service: SchoolService = Depends(get_school_service),
    coach_service: CoachService = Depends(get_coach_service),
):
    athlete = await athlete_service.get_athlete_with_details(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    school = None
    if athlete.school_id:
        school = await school_service.get_school(athlete.school_id)
    
    coach = None
    if athlete.coach_id:
        coach = await coach_service.get_coach(athlete.coach_id)
    
    personal_bests = {}
    for pb in athlete.personal_bests:
        key = f"{pb.distance}м {pb.stroke}"
        personal_bests[key] = pb
    
    return templates.TemplateResponse(
        "athlete_detail.html",
        {
            "request": request,
            "athlete": athlete,
            "school": school,
            "coach": coach,
            "personal_bests": personal_bests,
            "now": datetime.now(),
        },
    )


@router.get("/{athlete_id}")
async def get_athlete(
    athlete_id: int,
    service: AthleteService = Depends(get_athlete_service),
):
    athlete = await service.get_athlete_with_details(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.post("/{athlete_id}/personal-bests", response_model=PersonalBestResponse)
async def add_personal_best(
    athlete_id: int,
    data: PersonalBestCreate,
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    athlete = await service.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    if athlete.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    pb = await service.add_personal_best(
        athlete_id=athlete_id,
        distance=data.distance,
        stroke=data.stroke,
        time_seconds=data.time_seconds,
    )
    return pb



@router.delete("/personal-bests/{pb_id}")
async def delete_personal_best(
    pb_id: int,
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    """Удалить личный рекорд"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Получаем рекорд
    pb = await service.get_personal_best(pb_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Personal best not found")
    
    # Получаем спортсмена
    athlete = await service.get_athlete(pb.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # Проверяем права
    if athlete.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this record")
    
    deleted = await service.delete_personal_best(pb_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Personal best not found")
    return {"message": "Personal best deleted successfully"}

# ===== ЗАГРУЗКА АВАТАРА =====

from fastapi import UploadFile, File
from app.services.image_service import ImageService

@router.post("/{athlete_id}/upload-avatar")
async def upload_athlete_avatar(
    athlete_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить аватар спортсмена"""
    from app.services.athlete_service import AthleteService
    service = AthleteService(db)
    
    athlete = await service.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    
    if athlete.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(403, "Not authorized")
    
    url = await ImageService.save_image(file, "athletes", resize=(400, 400))
    await service.update_athlete(athlete_id, photo_url=url)
    
    return {"photo_url": url}

@router.post("/{athlete_id}/upload-cover")
async def upload_athlete_cover(
    athlete_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить обложку спортсмена"""
    from app.services.athlete_service import AthleteService
    service = AthleteService(db)
    
    athlete = await service.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    
    if athlete.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(403, "Not authorized")
    
    url = await ImageService.save_image(file, "athletes", resize=(1200, 400))
    await service.update_athlete(athlete_id, cover_url=url)
    
    return {"cover_url": url}
```

---

### `app/routers/athletes_fix.py`

```python
# Временно заменим зависимость
# В файле app/routers/athletes.py найдите строки с @router.get("/my/personal-bests")
# и замените current_user: User = Depends(get_current_active_user)
# на current_user: User = Depends(get_current_user_optional_cookie)
```

---

### `app/routers/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.csrf import generate_csrf_token, set_csrf_cookie
from app.core.csrf import verify_csrf_token
from app.auth import (
    get_current_active_user,
    get_current_user_from_cookie,
    get_current_user_optional_cookie,
)
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    ExpiredRefreshTokenError,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    Token,
    UserCreate,
    UserResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
)
from app.services.auth_service import AuthService
from app.core.rate_limit import limiter

# ===== СХЕМЫ ДЛЯ СБРОСА ПАРОЛЯ =====
from pydantic import BaseModel, EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/hour")
async def register(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
        )
        print(f"🔵 DEBUG: About to send welcome email to user {user.id}")

        await auth_service.send_welcome_email(user.id)
        print(f"🟢 DEBUG: Welcome email sent")

        return user

        # Отправляем приветственное письмо

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token, refresh_token = await auth_service.login_user(
            form_data.username, form_data.password
        )

        response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=1800,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=2592000,
        )

        csrf_token = generate_csrf_token()
        set_csrf_cookie(response, csrf_token)

        return response
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit("20/minute")
async def refresh_access_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token = await auth_service.refresh_access_token(
            refresh_data.refresh_token
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except (InvalidRefreshTokenError, ExpiredRefreshTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
@limiter.limit("20/minute")
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    verify_csrf_token(request)
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout(refresh_token)

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.post("/logout-all")
async def logout_all_devices(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout_all_devices(current_user.id)
    return {"message": "Logged out from all devices"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user_optional_cookie)):
    return current_user


# ===== ЭНДПОИНТЫ =====
@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(
    request: Request,
    data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Запрос на сброс пароля"""
    token = await auth_service.request_password_reset(data.email)
    await auth_service.send_password_reset_email(data.email, token)
    # Отправляем письмо со ссылкой для сброса

    return {"message": "If email exists, reset link sent"}


@router.post("/reset-password")
@limiter.limit("3/hour")
async def reset_password(
    request: Request,
    data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Подтверждение сброса пароля"""
    success = await auth_service.reset_password(data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_user: User = Depends(
        get_current_user_optional_cookie
    ),  # ← Поддерживает и cookie, и Bearer
    auth_service: AuthService = Depends(get_auth_service),
):
    # Проверяем CSRF только для cookie-аутентификации
    if request.cookies.get("access_token"):
        from app.core.csrf import verify_csrf_token

        verify_csrf_token(request)

    success = await auth_service.change_password(
        current_user.id, data.old_password, data.new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # После смены пароля удаляем старые токены
    response = JSONResponse(content={"message": "Password changed successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
```

---

### `app/routers/branches.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Branch, School

router = APIRouter(prefix="/branches", tags=["branches"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/{branch_id}/page")
async def branch_detail_page(
    branch_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Получаем филиал
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Получаем школу
    school_result = await db.execute(
        select(School).where(School.id == branch.school_id)
    )
    school = school_result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "branch_detail.html",
        {
            "request": request,
            "branch": branch,
            "school": school
        }
    )

@router.get("/{branch_id}/coaches")
async def get_branch_coaches(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить тренеров филиала (API)"""
    from sqlalchemy.orm import selectinload
    from app.models import CoachProfile, User
    
    result = await db.execute(
        select(CoachProfile)
        .options(selectinload(CoachProfile.user))
        .where(CoachProfile.branch_id == branch_id)
    )
    coaches = result.scalars().all()
    
    return [
        {
            "id": coach.id,
            "full_name": coach.user.full_name if coach.user else "Unknown",
            "qualification": coach.qualification,
            "experience_years": coach.experience_years,
            "specialization": coach.specialization,
            "is_head_coach": coach.is_head_coach,
            "photo_url": coach.photo_url
        }
        for coach in coaches
    ]
```

---

### `app/routers/chat.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text
import json
from datetime import datetime, timezone
from app.database import async_session_maker
from app.core.logging_config import logger

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[tuple[WebSocket, int, str]]] = {}

    async def connect(self, websocket: WebSocket, room: str, user_id: int, username: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append((websocket, user_id, username))
        logger.info(f"✅ WebSocket connected: user {username} (ID: {user_id}) to room {room}")
        
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to room {room}",
            "user": username
        })

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room] = [
                (ws, uid, name) for ws, uid, name in self.active_connections[room] if ws != websocket
            ]
            if not self.active_connections[room]:
                del self.active_connections[room]
        logger.info(f"❌ WebSocket disconnected from {room}")

    async def broadcast_to_room(self, room: str, message: dict, exclude_user_id: int = None):
        if room not in self.active_connections:
            return
        
        for connection, user_id, username in self.active_connections[room]:
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to user {username}: {e}")


manager = ConnectionManager()


@router.websocket("/ws/chat/{room}")
async def websocket_chat(
    websocket: WebSocket,
    room: str,
):
    # Для разработки - создаем тестового пользователя если нет токена
    # В production нужно использовать реальную аутентификацию
    await websocket.accept()
    
    # Временно используем тестового пользователя для отладки
    test_user_id = 1
    test_username = "TestUser"
    
    logger.info(f"WebSocket connected with test user: {test_username} to room {room}")
    await manager.connect(websocket, room, test_user_id, test_username)
    
    # Загружаем историю сообщений
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                text("""
                    SELECT cm.id, cm.message, cm.created_at, u.username
                    FROM chat_messages cm
                    JOIN "user" u ON u.id = cm.user_id
                    WHERE cm.room = :room
                    ORDER BY cm.created_at DESC
                    LIMIT 50
                """),
                {"room": room}
            )
            rows = result.fetchall()
            
            for row in reversed(rows):
                await websocket.send_json({
                    "type": "history",
                    "user": row.username,
                    "message": row.message,
                    "created_at": row.created_at.isoformat() if row.created_at else "",
                })
        except Exception as e:
            logger.error(f"Error loading history: {e}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_text = message_data.get("message", "").strip()
            
            if not message_text:
                continue
            
            logger.info(f"Received message from {test_username}: {message_text[:50]}")
            
            # Сохраняем сообщение
            async with async_session_maker() as db:
                try:
                    now = datetime.now(timezone.utc)
                    await db.execute(
                        text("""
                            INSERT INTO chat_messages (room, user_id, message, created_at)
                            VALUES (:room, :user_id, :message, :created_at)
                        """),
                        {
                            "room": room,
                            "user_id": test_user_id,
                            "message": message_text,
                            "created_at": now
                        }
                    )
                    await db.commit()
                    
                    broadcast_message = {
                        "type": "message",
                        "user": test_username,
                        "message": message_text,
                        "created_at": now.isoformat(),
                    }
                    
                    await manager.broadcast_to_room(room, broadcast_message)
                    
                except Exception as e:
                    logger.error(f"Error saving message: {e}")
                    await db.rollback()
                    
    except WebSocketDisconnect:
        logger.info(f"User {test_username} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, room)
```

---

### `app/routers/coach_dashboard.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, UserRole
from app.core.logging_config import logger

router = APIRouter(prefix="/coach", tags=["coach"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def coach_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Панель управления тренера"""
    
    # Проверяем, что пользователь - тренер
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="Access denied. Coach only.")
    
    # Получаем профиль тренера
    result = await db.execute(
        text("""
            SELECT cp.*, s.name as school_name
            FROM coach_profiles cp
            LEFT JOIN schools s ON s.id = cp.school_id
            WHERE cp.user_id = :user_id
        """),
        {"user_id": current_user.id}
    )
    coach_profile = result.fetchone()
    
    if not coach_profile:
        # Создаем профиль тренера если нет
        result = await db.execute(
            text("""
                INSERT INTO coach_profiles (user_id, experience_years)
                VALUES (:user_id, 0)
                RETURNING id
            """),
            {"user_id": current_user.id}
        )
        await db.commit()
        coach_id = result.scalar()
    else:
        coach_id = coach_profile.id
    
    # Получаем список учеников
    students_result = await db.execute(
        text("""
            SELECT 
                u.id, u.full_name, u.email,
                a.birth_date, a.gender, a.rank,
                s.name as school_name,
                (
                    SELECT COUNT(*) 
                    FROM entries e 
                    JOIN heat_entries he ON he.entry_id = e.id 
                    WHERE e.athlete_id = a.id AND he.result_time IS NOT NULL
                ) as races_count,
                (
                    SELECT MIN(he.result_time) 
                    FROM entries e 
                    JOIN heat_entries he ON he.entry_id = e.id 
                    WHERE e.athlete_id = a.id AND he.result_time IS NOT NULL
                ) as best_time
            FROM athlete_profiles a
            JOIN "user" u ON u.id = a.user_id
            LEFT JOIN schools s ON s.id = a.school_id
            WHERE a.coach_id = :coach_id
            ORDER BY u.full_name
        """),
        {"coach_id": coach_id}
    )
    students = students_result.fetchall()
    
    # Получаем статистику
    stats_result = await db.execute(
        text("""
            SELECT 
                COUNT(DISTINCT a.id) as total_students,
                COUNT(DISTINCT e.competition_id) as total_competitions,
                COUNT(he.id) as total_races,
                AVG(he.place) as avg_place
            FROM coach_profiles cp
            JOIN athlete_profiles a ON a.coach_id = cp.id
            LEFT JOIN entries e ON e.athlete_id = a.id
            LEFT JOIN heat_entries he ON he.entry_id = e.id
            WHERE cp.id = :coach_id
        """),
        {"coach_id": coach_id}
    )
    stats = stats_result.fetchone()
    
    return templates.TemplateResponse(
        "coach_dashboard.html",
        {
            "request": request,
            "coach": coach_profile,
            "students": students,
            "stats": stats,
            "current_user": current_user
        }
    )


@router.get("/student/{student_id}")
async def student_details(
    student_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Детали ученика для тренера"""
    
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем данные ученика
    result = await db.execute(
        text("""
            SELECT 
                u.id, u.full_name, u.email, u.username,
                a.birth_date, a.gender, a.rank,
                s.name as school_name
            FROM athlete_profiles a
            JOIN "user" u ON u.id = a.user_id
            LEFT JOIN schools s ON s.id = a.school_id
            WHERE a.id = :student_id
        """),
        {"student_id": student_id}
    )
    student = result.fetchone()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Получаем результаты ученика
    results = await db.execute(
        text("""
            SELECT 
                c.name as competition_name,
                c.start_date,
                se.name as event_name,
                se.distance,
                se.stroke,
                he.result_time,
                he.place
            FROM entries e
            JOIN swim_events se ON se.id = e.swim_event_id
            JOIN competitions c ON c.id = se.competition_id
            JOIN heat_entries he ON he.entry_id = e.id
            WHERE e.athlete_id = :student_id AND he.result_time IS NOT NULL
            ORDER BY c.start_date DESC
            LIMIT 20
        """),
        {"student_id": student_id}
    )
    
    return templates.TemplateResponse(
        "coach_student_detail.html",
        {
            "request": request,
            "student": student,
            "results": results.fetchall()
        }
    )
```

---

### `app/routers/coach_profiles.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.services.coach_service import CoachService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/coach-profiles", tags=["coach-profiles"])


def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)


class CoachProfileCreate(BaseModel):
    user_id: int
    school_id: Optional[int] = None
    qualification: Optional[str] = None
    experience_years: int = 0
    specialization: Optional[str] = None
    is_head_coach: bool = False
    bio: Optional[str] = None
    achievements: Optional[str] = None
    photo_url: Optional[str] = None
    birth_date: Optional[datetime] = None


class CoachProfileResponse(BaseModel):
    id: int
    user_id: int
    school_id: Optional[int]
    qualification: Optional[str]
    experience_years: int
    specialization: Optional[str]
    is_head_coach: bool
    bio: Optional[str]
    achievements: Optional[str]
    photo_url: Optional[str]
    birth_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=CoachProfileResponse)
async def create_coach_profile(
    data: CoachProfileCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHOOL_REP])),
    service: CoachService = Depends(get_coach_service),
):
    """Создать профиль тренера"""
    return await service.create_coach_profile(**data.model_dump())
```

---

### `app/routers/coaches.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.coach_service import CoachService
from app.services.school_service import SchoolService
from app.services.athlete_service import AthleteService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/coaches", tags=["coaches"])
templates = Jinja2Templates(directory="app/templates")


def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)


def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


def get_athlete_service(db: AsyncSession = Depends(get_db)) -> AthleteService:
    return AthleteService(db)


class CoachResponse(BaseModel):
    id: int
    user_id: int
    school_id: int | None
    photo_url: str | None
    bio: str | None
    birth_date: datetime | None
    qualification: str | None
    experience_years: int
    specialization: str | None
    is_head_coach: bool
    achievements: str | None

    class Config:
        from_attributes = True


# Страница деталей тренера
@router.get("/{coach_id}/page")
async def coach_detail_page(
    coach_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    coach_service = CoachService(db)
    school_service = SchoolService(db)
    athlete_service = AthleteService(db)
    
    coach = await coach_service.get_coach(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    school = None
    if coach.school_id:
        school = await school_service.get_school(coach.school_id)
    
    # Получаем учеников тренера
    from sqlalchemy import select
    from app.models import AthleteProfile, User
    
    result = await db.execute(
        select(AthleteProfile)
        .options(selectinload(AthleteProfile.user))
        .where(AthleteProfile.coach_id == coach_id)
    )
    athletes = result.scalars().all()
    
    return templates.TemplateResponse("coach_detail.html", {
        "request": request,
        "coach": coach,
        "school": school,
        "athletes": athletes,
        "now": datetime.now()
    })


# API для получения тренера
@router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(
    coach_id: int,
    service: CoachService = Depends(get_coach_service),
):
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach

# ===== ЗАГРУЗКА АВАТАРА =====

from fastapi import UploadFile, File
from app.services.image_service import ImageService

@router.post("/{coach_id}/upload-avatar")
async def upload_coach_avatar(
    coach_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COACH, UserRole.SCHOOL_REP])),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить аватар тренера"""
    from app.services.coach_service import CoachService
    service = CoachService(db)
    
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(404, "Coach not found")
    
    # Проверяем права
    if coach.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SCHOOL_REP]:
        raise HTTPException(403, "Not authorized")
    
    url = await ImageService.save_image(file, "coaches", resize=(400, 400))
    await service.update_coach(coach_id, photo_url=url)
    
    return {"photo_url": url}

@router.post("/{coach_id}/upload-cover")
async def upload_coach_cover(
    coach_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COACH, UserRole.SCHOOL_REP])),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить обложку тренера"""
    from app.services.coach_service import CoachService
    service = CoachService(db)
    
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(404, "Coach not found")
    
    if coach.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SCHOOL_REP]:
        raise HTTPException(403, "Not authorized")
    
    url = await ImageService.save_image(file, "coaches", resize=(1200, 400))
    await service.update_coach(coach_id, cover_url=url)
    
    return {"cover_url": url}
```

---

### `app/routers/competitions.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.core.cache import cached, delete_cache, clear_cache_pattern
from app.database import get_db
from app.services.competition_service import CompetitionService
from app.auth import get_current_active_user
from app.models import User
from app.core.dependencies import require_role
from app.models import UserRole
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from urllib.parse import unquote
from fastapi.responses import StreamingResponse
from app.services.pdf_service import PDFService

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/competitions", tags=["competitions"])


def get_competition_service(db: AsyncSession = Depends(get_db)) -> CompetitionService:
    return CompetitionService(db)


# Схемы для запросов/ответов
class CompetitionCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: datetime
    end_date: datetime
    venue: str | None = None
    city: str | None = None
    status: str = "draft"
    max_participants: int = 0


class CompetitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    venue: str | None = None
    city: str | None = None
    status: str | None = None
    max_participants: int | None = None


class CompetitionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: datetime
    end_date: datetime
    venue: str | None
    city: str | None
    status: str
    max_participants: int
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/page")
async def competitions_page(
    request: Request,
    service: CompetitionService = Depends(get_competition_service),
):
    competitions = await service.get_all_competitions()
    return templates.TemplateResponse(
        "competitions_list.html", {"request": request, "competitions": competitions}
    )


@router.get("/search")
async def search_competitions(
    request: Request,
    name: str = "",
    city: str = "",
    status: str = "",
    page: int = 1,
    service: CompetitionService = Depends(get_competition_service),
):
    name = unquote(name)
    city = unquote(city)
    status = unquote(status)

    result = await service.search_competitions(name, city, status, page)
    return templates.TemplateResponse(
        "partials/competition_items.html",
        {
            "request": request,
            "competitions": result["items"],
            "page": page,
            "total": result["total"],
            "pages": result["pages"],
        },
    )


@router.get("/active", response_model=List[CompetitionResponse])
async def get_active_competitions(
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_active_competitions()


@router.get("/upcoming", response_model=List[CompetitionResponse])
async def get_upcoming_competitions(
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_upcoming_competitions()


@router.post("/", response_model=CompetitionResponse)
async def create_competition(
    competition_data: CompetitionCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    competition = await service.create_competition(
        name=competition_data.name,
        description=competition_data.description,
        start_date=competition_data.start_date,
        end_date=competition_data.end_date,
        venue=competition_data.venue,
        city=competition_data.city,
        status=competition_data.status,
        max_participants=competition_data.max_participants,
        created_by=current_user.id,
    )
    return competition


@router.get("/", response_model=List[CompetitionResponse])
@cached(expire=60, key_prefix="competitions_list")
async def get_all_competitions(
    skip: int = 0,
    limit: int = 100,
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_all_competitions(skip, limit)


@router.get("/{competition_id}", response_model=CompetitionResponse)
@cached(expire=300, key_prefix="competition_detail")
async def get_competition(
    competition_id: int,
    service: CompetitionService = Depends(get_competition_service),
):
    competition = await service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition


@router.put("/{competition_id}", response_model=CompetitionResponse)
async def update_competition(
    competition_id: int,
    competition_data: CompetitionUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    update_data = {
        k: v for k, v in competition_data.model_dump().items() if v is not None
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    competition = await service.update_competition(competition_id, **update_data)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Очищаем кэш
    await clear_cache_pattern("competition_list*")
    await clear_cache_pattern(f"competition_detail:{competition_id}*")

    return competition


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    deleted = await service.delete_competition(competition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Competition not found")
    return {"message": "Competition deleted successfully"}


@router.get("/{competition_id}/page")
async def competition_detail_page(
    competition_id: int,
    request: Request,
    service: CompetitionService = Depends(get_competition_service),
):
    competition = await service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return templates.TemplateResponse(
        "competition_detail.html", {"request": request, "competition": competition}
    )


@router.get("/{competition_id}/start-list.pdf")
async def download_start_list(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    pdf_buffer = await PDFService.generate_start_list(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=start_list_{competition_id}.pdf"
        },
    )


@router.get("/{competition_id}/results.pdf")
async def download_results_protocol(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    pdf_buffer = await PDFService.generate_results_protocol(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=results_{competition_id}.pdf"
        },
    )


@router.get("/cached-list")
@cached(expire=60, key_prefix="competitions_list")
async def get_all_competitions_cached(
    skip: int = 0,
    limit: int = 100,
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_all_competitions(skip, limit)


@router.get("/test-cache")
@cached(expire=30, key_prefix="test")
async def test_cache():
    import time
    return {"timestamp": time.time(), "message": "Cached response"}


@router.get("/{competition_id}/results.csv")
async def download_results_csv(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Скачать результаты соревнования в CSV"""
    from app.services.csv_service import CSVService
    
    csv_buffer = await CSVService.export_competition_results(competition_id, db)
    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=results_{competition_id}.csv"
        },
    )
```

---

### `app/routers/entries.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from fastapi import UploadFile, File
from app.database import get_db
from app.services.entry_service import EntryService
from app.models import User, UserRole
from app.core.dependencies import require_role
from app.auth import get_current_active_user
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from app.services.competition_service import CompetitionService
from datetime import datetime


def get_competition_service(db: AsyncSession = Depends(get_db)) -> CompetitionService:
    return CompetitionService(db)


router = APIRouter(prefix="/entries", tags=["entries"])


def get_entry_service(db: AsyncSession = Depends(get_db)) -> EntryService:
    return EntryService(db)


# Схемы
class EntryCreate(BaseModel):
    competition_id: int
    swim_event_id: int
    athlete_id: int
    entry_time: float | None = None
    status: str = "pending"


class EntryUpdate(BaseModel):
    status: str | None = None
    entry_time: float | None = None


class EntryResponse(BaseModel):
    id: int
    competition_id: int
    swim_event_id: int
    athlete_id: int
    status: str
    entry_time: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=EntryResponse)
async def create_entry(
    data: EntryCreate,
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH])
    ),
    service: EntryService = Depends(get_entry_service),
):
    """Создать заявку (ADMIN, SECRETARY, COACH)"""
    entry = await service.create_entry(**data.model_dump())
    return entry


@router.get("/competition/{competition_id}", response_model=List[EntryResponse])
async def get_entries_by_competition(
    competition_id: int,
    service: EntryService = Depends(get_entry_service),
):
    """Получить заявки для соревнования"""
    return await service.get_entries_by_competition(competition_id)


@router.get("/swim-event/{swim_event_id}", response_model=List[EntryResponse])
async def get_entries_by_swim_event(
    swim_event_id: int,
    service: EntryService = Depends(get_entry_service),
):
    """Получить заявки для дистанции"""
    return await service.get_entries_by_swim_event(swim_event_id)


@router.get("/athlete/{athlete_id}", response_model=List[EntryResponse])
async def get_entries_by_athlete(
    athlete_id: int,
    current_user: User = Depends(
        require_role(
            [UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH, UserRole.ATHLETE]
        )
    ),
    service: EntryService = Depends(get_entry_service),
):
    """Получить заявки спортсмена (ADMIN, SECRETARY, COACH, ATHLETE)"""
    # Простая проверка: если пользователь не админ и не секретарь,
    # он может видеть только свои заявки (нужно связать athlete_id с user_id)
    return await service.get_entries_by_athlete(athlete_id)


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: int,
    service: EntryService = Depends(get_entry_service),
):
    entry = await service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: int,
    data: EntryUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: EntryService = Depends(get_entry_service),
):
    """Обновить заявку (ADMIN, SECRETARY)"""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    entry = await service.update_entry_status(entry_id, update_data.get("status"))
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: EntryService = Depends(get_entry_service),
):
    """Удалить заявку (ADMIN, SECRETARY)"""
    deleted = await service.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}


@router.get("/template/{competition_id}")
async def download_entry_template(
    competition_id: int,
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH])
    ),
    entry_service: EntryService = Depends(get_entry_service),
    competition_service: CompetitionService = Depends(get_competition_service),
):
    competition = await competition_service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    output = await entry_service.generate_excel_template(competition_id)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=entries_template_{competition_id}.xlsx"
        },
    )


@router.post("/upload/{competition_id}")
async def upload_entries_excel(
    competition_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH])
    ),
    entry_service: EntryService = Depends(get_entry_service),
    competition_service: CompetitionService = Depends(get_competition_service),
):
    # Проверяем, существует ли соревнование
    competition = await competition_service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Проверяем расширение файла
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="File must be Excel format (.xlsx or .xls)"
        )

    # Читаем файл и передаём в сервис
    contents = await file.read()
    result = await entry_service.import_from_excel(competition_id, contents)

    if result.get("errors"):
        raise HTTPException(status_code=400, detail=result)

    return result
```

---

### `app/routers/heats.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.heat_service import HeatService
from app.models import User, UserRole
from app.core.dependencies import require_role
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/heats", tags=["heats"])


def get_heat_service(db: AsyncSession = Depends(get_db)) -> HeatService:
    return HeatService(db)


class HeatResponse(BaseModel):
    id: int
    swim_event_id: int
    heat_number: int
    lane_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class HeatEntryResponse(BaseModel):
    id: int
    heat_id: int
    entry_id: int
    lane: int
    result_time: float | None
    place: int | None

    class Config:
        from_attributes = True


class ResultInput(BaseModel):
    result_time: float


@router.post("/generate/{swim_event_id}")
async def generate_heats(
    swim_event_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: HeatService = Depends(get_heat_service),
):
    """Сгенерировать заплывы для дистанции"""
    result = await service.generate_heats(swim_event_id)
    return result


@router.get("/swim-event/{swim_event_id}", response_model=List[HeatResponse])
async def get_heats_by_swim_event(
    swim_event_id: int,
    service: HeatService = Depends(get_heat_service),
):
    return await service.get_heats_by_swim_event(swim_event_id)


@router.post("/entry/{heat_entry_id}/result")
async def set_result(
    heat_entry_id: int,
    data: ResultInput,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: HeatService = Depends(get_heat_service),
):
    """Ввести результат для участника (ADMIN, SECRETARY)"""
    try:
        heat_entry = await service.enter_result(heat_entry_id, data.result_time)
        return {"message": "Result saved", "heat_entry": heat_entry}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/heat/{heat_id}/complete")
async def complete_heat(
    heat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: HeatService = Depends(get_heat_service),
):
    """Завершить заплыв и рассчитать места (ADMIN, SECRETARY)"""
    try:
        heat = await service.complete_heat(heat_id)
        return {"message": "Heat completed", "heat": heat}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/heat/{heat_id}/results")
async def get_heat_results(
    heat_id: int,
    service: HeatService = Depends(get_heat_service),
):
    entries = await service.get_heat_results(heat_id)
    entries_sorted = sorted(entries, key=lambda e: e.place if e.place else 999)
    return [
        {
            "lane": e.lane,
            "entry_id": e.entry_id,
            "result_time": e.result_time,
            "place": e.place,
        }
        for e in entries_sorted
    ]


@router.get("/live/{competition_id}/events")
async def live_results_stream(
    competition_id: int,
    service: HeatService = Depends(get_heat_service),
):
    """SSE поток для live-таблицы результатов"""

    async def event_generator():
        while True:
            # Получаем актуальные результаты из сервиса
            results = await service.get_live_results(competition_id)

            # Отправляем событие с данными
            yield f"data: {json.dumps(results, default=str)}\n\n"

            await asyncio.sleep(2)  # Обновление каждые 2 секунды

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

---

### `app/routers/news.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.news_service import NewsService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/news", tags=["news"])
templates = Jinja2Templates(directory="app/templates")


def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(db)


class NewsCreate(BaseModel):
    title: str
    content: str


class NewsUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int | None
    is_published: bool
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/test-page")
async def test_page(request: Request):
    return HTMLResponse("<h1>News page works!</h1>")


@router.get("/page")
async def news_page(request: Request):
    return templates.TemplateResponse("news_list.html", {"request": request})


@router.get("/search")
async def search_news(
    request: Request,
    q: str = "",
    sort: str = "newest",
    page: int = 1,
    service: NewsService = Depends(get_news_service),
):
    result = await service.search_news(q, sort, page)
    return templates.TemplateResponse(
        "partials/news_items.html",
        {
            "request": request,
            "news_list": result["items"],
            "q": q,
            "page": page,
            "sort": sort,
            "total": result["total"],
            "pages": result["pages"],
        },
    )


@router.post("/", response_model=NewsResponse)
async def create_news(
    data: NewsCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    return await service.create_news(
        title=data.title, content=data.content, author_id=current_user.id
    )


@router.post("/{news_id}/publish", response_model=NewsResponse)
async def publish_news(
    news_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    news = await service.publish_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.get("/", response_model=List[NewsResponse])
async def get_all_news(
    skip: int = 0,
    limit: int = 100,
    service: NewsService = Depends(get_news_service),
):
    return await service.get_all_published(skip, limit)


@router.get("/{news_id}")
async def get_news(
    news_id: int,
    request: Request,
    service: NewsService = Depends(get_news_service),
):
    news = await service.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return templates.TemplateResponse(
        "news_detail.html", {"request": request, "news": news}
    )


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    data: NewsUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    news = await service.update_news(news_id, **update_data)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    deleted = await service.delete_news(news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
    return {"message": "News deleted successfully"}
```

---

### `app/routers/schools.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.school_service import SchoolService
from app.models import User, UserRole, CoachProfile, Branch
from app.core.dependencies import require_role

router = APIRouter(prefix="/schools", tags=["schools"])
templates = Jinja2Templates(directory="app/templates")

def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)

@router.get("/{school_id}/page")
async def school_detail_page(
    school_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    school_service = SchoolService(db)
    
    school = await school_service.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Получаем филиалы школы
    branches = await school_service.get_branches(school_id)
    
    # Получаем главного тренера школы (is_head_coach = True)
    head_coach_result = await db.execute(
        select(CoachProfile)
        .options(selectinload(CoachProfile.user))
        .where(CoachProfile.school_id == school_id, CoachProfile.is_head_coach == True)
    )
    head_coach = head_coach_result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "school_detail.html", 
        {
            "request": request, 
            "school": school, 
            "branches": branches,
            "head_coach": head_coach,
            "now": datetime.now()
        }
    )

# ... остальные эндпоинты (GET, POST, PUT, DELETE) остаются без изменений ...
```

---

### `app/routers/swim_events.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.swim_event_service import SwimEventService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/swim-events", tags=["swim-events"])


def get_swim_event_service(db: AsyncSession = Depends(get_db)) -> SwimEventService:
    return SwimEventService(db)


class SwimEventCreate(BaseModel):
    competition_id: int
    name: str
    distance: int
    stroke: str
    gender: str | None = None
    is_relay: bool = False
    order: int = 0


class SwimEventUpdate(BaseModel):
    name: str | None = None
    distance: int | None = None
    stroke: str | None = None
    gender: str | None = None
    is_relay: bool | None = None
    order: int | None = None


class SwimEventResponse(BaseModel):
    id: int
    competition_id: int
    name: str
    distance: int
    stroke: str
    gender: str | None
    is_relay: bool
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=SwimEventResponse)
async def create_swim_event(
    data: SwimEventCreate,
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: SwimEventService = Depends(get_swim_event_service),
):
    return await service.create_swim_event(**data.model_dump())


@router.get("/competition/{competition_id}", response_model=List[SwimEventResponse])
async def get_swim_events_by_competition(
    competition_id: int,
    service: SwimEventService = Depends(get_swim_event_service),
):
    return await service.get_by_competition(competition_id)


@router.get("/{event_id}", response_model=SwimEventResponse)
async def get_swim_event(
    event_id: int,
    service: SwimEventService = Depends(get_swim_event_service),
):
    event = await service.get_swim_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Swim event not found")
    return event


@router.put("/{event_id}", response_model=SwimEventResponse)
async def update_swim_event(
    event_id: int,
    data: SwimEventUpdate,
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: SwimEventService = Depends(get_swim_event_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    event = await service.update_swim_event(event_id, **update_data)
    if not event:
        raise HTTPException(status_code=404, detail="Swim event not found")
    return event


@router.delete("/{event_id}")
async def delete_swim_event(
    event_id: int,
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: SwimEventService = Depends(get_swim_event_service),
):
    deleted = await service.delete_swim_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Swim event not found")
    return {"message": "Swim event deleted successfully"}
```

---

### `app/schemas/__init__.py`

```python
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, TokenData, RefreshTokenRequest, RefreshTokenResponse, LogoutRequest

__all__ = [
    "UserCreate",
    "UserResponse",
    "Token",
    "TokenData",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "LogoutRequest",
]
```

---

### `app/schemas/token.py`

```python
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
```

---

### `app/schemas/user.py`

```python
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
```

---

### `app/services/age_category_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.age_category_repository import AgeCategoryRepository
from app.models import AgeCategory


class AgeCategoryService:
    """Сервис для работы с возрастными категориями"""

    def __init__(self, session: AsyncSession):
        self.repo = AgeCategoryRepository(session)

    async def create_age_category(
        self,
        competition_id: int,
        name: str,
        min_age: int,
        max_age: int,
        gender: Optional[str] = None,
    ) -> AgeCategory:
        """Создать возрастную категорию для соревнования"""
        return await self.repo.create(
            competition_id=competition_id,
            name=name,
            min_age=min_age,
            max_age=max_age,
            gender=gender,
        )

    async def get_age_category(self, category_id: int) -> Optional[AgeCategory]:
        """Получить возрастную категорию по ID"""
        return await self.repo.get_by_id(category_id)

    async def get_categories_by_competition(
        self, competition_id: int
    ) -> List[AgeCategory]:
        """Получить все категории для соревнования"""
        return await self.repo.get_by_competition(competition_id)

    async def update_age_category(
        self, category_id: int, **kwargs
    ) -> Optional[AgeCategory]:
        """Обновить возрастную категорию"""
        return await self.repo.update(category_id, **kwargs)

    async def delete_age_category(self, category_id: int) -> bool:
        """Удалить возрастную категорию"""
        return await self.repo.delete(category_id)
```

---

### `app/services/article_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.article_repository import ArticleRepository
from app.models import Article


class ArticleService:
    def __init__(self, session: AsyncSession):
        self.repo = ArticleRepository(session)

    async def create_article(
        self,
        title: str,
        content: str,
        category: str,
        author_id: int,
        summary: Optional[str] = None,
    ) -> Article:
        return await self.repo.create(
            title=title,
            content=content,
            category=category,
            summary=summary,
            author_id=author_id,
        )

    async def publish_article(self, article_id: int) -> Optional[Article]:
        from datetime import datetime, timezone

        return await self.repo.update(
            article_id, is_published=True, published_at=datetime.now(timezone.utc)
        )

    async def get_article(self, article_id: int) -> Optional[Article]:
        return await self.repo.get_by_id(article_id)

    async def get_all_published(self, skip: int = 0, limit: int = 100) -> List[Article]:
        return await self.repo.get_published(skip, limit)

    async def get_by_category(self, category: str) -> List[Article]:
        return await self.repo.get_by_category(category)

    async def increment_views(self, article_id: int) -> None:
        await self.repo.increment_views(article_id)

    async def update_article(self, article_id: int, **kwargs) -> Optional[Article]:
        return await self.repo.update(article_id, **kwargs)

    async def delete_article(self, article_id: int) -> bool:
        return await self.repo.delete(article_id)

    async def search_articles(
        self, query: str = "", category: str = "", page: int = 1
    ) -> dict:
        return await self.repo.search(query, category, page)
```

---

### `app/services/athlete_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.athlete_profile_repository import AthleteProfileRepository
from app.repositories.personal_best_repository import PersonalBestRepository
from app.models import AthleteProfile, PersonalBest


class AthleteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AthleteProfileRepository(session)
        self.pb_repo = PersonalBestRepository(session)

    async def create_athlete_profile(
        self,
        user_id: int,
        school_id: Optional[int] = None,
        coach_id: Optional[int] = None,
        birth_date: Optional[str] = None,
        gender: Optional[str] = None,
        rank: Optional[str] = None,
        photo_url: Optional[str] = None,
    ) -> AthleteProfile:
        return await self.repo.create(
            user_id=user_id,
            school_id=school_id,
            coach_id=coach_id,
            birth_date=birth_date,
            gender=gender,
            rank=rank,
            photo_url=photo_url,
        )

    async def get_athlete(self, athlete_id: int) -> Optional[AthleteProfile]:
        return await self.repo.get_by_id(athlete_id)

    async def get_athlete_with_details(self, athlete_id: int) -> Optional[AthleteProfile]:
        return await self.repo.get_by_id_with_details(athlete_id)

    async def get_athlete_by_user_id(self, user_id: int) -> Optional[AthleteProfile]:
        return await self.repo.get_by_user_id(user_id)

    async def get_athletes_by_school(self, school_id: int) -> List[AthleteProfile]:
        return await self.repo.get_by_school(school_id)

    async def update_athlete(self, athlete_id: int, **kwargs) -> Optional[AthleteProfile]:
        return await self.repo.update(athlete_id, **kwargs)

    async def delete_athlete(self, athlete_id: int) -> bool:
        return await self.repo.delete(athlete_id)

    async def add_personal_best(
        self,
        athlete_id: int,
        distance: int,
        stroke: str,
        time_seconds: float,
    ) -> PersonalBest:
        """Добавить личный рекорд"""
        return await self.pb_repo.create(
            athlete_id=athlete_id,
            distance=distance,
            stroke=stroke,
            time_seconds=time_seconds,
        )
    
    async def get_personal_bests(self, athlete_id: int) -> List[PersonalBest]:
        """Получить все личные рекорды спортсмена"""
        return await self.pb_repo.get_by_athlete(athlete_id)
    
    async def delete_personal_best(self, pb_id: int) -> bool:
        """Удалить личный рекорд"""
        return await self.pb_repo.delete(pb_id)


    async def get_personal_best(self, pb_id: int) -> Optional[PersonalBest]:
        """Получить личный рекорд по ID"""
        return await self.pb_repo.get_by_id(pb_id)
```

---

### `app/services/auth_service.py`

```python
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    ExpiredRefreshTokenError,
)
from app.models import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.password_reset_repository import PasswordResetRepository


class AuthService:
    """Сервис для аутентификации (бизнес-логика)"""

    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)
        self.session = session

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role: UserRole,
    ):
        """Зарегистрировать нового пользователя"""
        if await self.user_repo.get_by_email(email):
            raise UserAlreadyExistsError("email", email)

        if await self.user_repo.get_by_username(username):
            raise UserAlreadyExistsError("username", username)

        hashed_password = get_password_hash(password)
        user = await self.user_repo.create(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
        )
        return user

    async def login_user(self, username: str, password: str) -> tuple[str, str]:
        """Возвращает (access_token, refresh_token)"""
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        # Создаём access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )

        # Создаём refresh token
        refresh_token_obj = await self.refresh_token_repo.create_token(user.id)

        return access_token, refresh_token_obj.token

    async def refresh_access_token(self, refresh_token_value: str) -> str:
        """Обновить access token по refresh token"""
        refresh_token = await self.refresh_token_repo.get_by_token(refresh_token_value)
        if not refresh_token:
            raise InvalidRefreshTokenError("Invalid refresh token")

        now = datetime.now(timezone.utc)
        if refresh_token.expires_at < now:
            await self.refresh_token_repo.revoke_token(refresh_token.id)
            raise ExpiredRefreshTokenError("Refresh token expired")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(refresh_token.user_id)},
            expires_delta=access_token_expires,
        )
        return access_token

    async def logout(self, refresh_token_value: str) -> None:
        """Отозвать refresh token"""
        refresh_token = await self.refresh_token_repo.get_by_token(refresh_token_value)
        if refresh_token:
            await self.refresh_token_repo.revoke_token(refresh_token.id)

    async def logout_all_devices(self, user_id: int) -> None:
        """Отозвать все refresh токены пользователя"""
        await self.refresh_token_repo.revoke_all_user_tokens(user_id)

    async def request_password_reset(self, email: str) -> str:
        """Создаёт токен для сброса пароля. Возвращает токен."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return "reset_token_placeholder"
        
        self.password_reset_repo = PasswordResetRepository(self.session)
        token = await self.password_reset_repo.create_token(user.id)
        return token.token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Сброс пароля по токену."""
        self.password_reset_repo = PasswordResetRepository(self.session)
        
        reset_token = await self.password_reset_repo.get_valid_token(token)
        if not reset_token:
            return False
        
        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            return False
        
        hashed_password = get_password_hash(new_password)
        await self.user_repo.update(user.id, hashed_password=hashed_password)
        await self.password_reset_repo.mark_as_used(reset_token.id)
        
        # Отзываем все refresh токены пользователя
        await self.refresh_token_repo.revoke_all_user_tokens(user.id)
        
        return True

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Смена пароля авторизованным пользователем."""
        user = await self.user_repo.get_by_id(user_id)
        if not user or not verify_password(old_password, user.hashed_password):
            return False
        
        hashed_password = get_password_hash(new_password)
        await self.user_repo.update(user_id, hashed_password=hashed_password)
        
        # Отзываем все refresh токены
        await self.refresh_token_repo.revoke_all_user_tokens(user_id)
        
        return True

    async def send_welcome_email(self, user_id: int) -> None:
        """Отправить приветственное письмо"""
        user = await self.user_repo.get_by_id(user_id)
        if user and user.email:
            from app.core.email import send_welcome_email
            await send_welcome_email(user.email, user.username)

    async def send_password_reset_email(self, email: str, token: str) -> None:
        """Отправить письмо со ссылкой для сброса пароля"""
        from app.core.email import send_password_reset_email
        await send_password_reset_email(email, token)
```

---

### `app/services/chat_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.models import ChatMessage, User
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatMessage]):
    def __init__(self, session: AsyncSession):
        super().__init__(ChatMessage, session)

    async def get_messages(self, room: str, limit: int = 50) -> List[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.room == room)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def can_access_room(self, user: User, room: str) -> bool:
        """Проверка прав доступа к комнате"""
        if not user:
            return False
        # Все зарегистрированные пользователи могут писать в любые комнаты
        return True


class ChatService:
    def __init__(self, session: AsyncSession):
        self.repo = ChatRepository(session)

    async def save_message(self, room: str, user_id: int, message: str) -> ChatMessage:
        return await self.repo.create(room=room, user_id=user_id, message=message)

    async def get_messages(self, room: str, user: User) -> List[ChatMessage]:
        if not await self.repo.can_access_room(user, room):
            return []
        return await self.repo.get_messages(room)
```

---

### `app/services/coach_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.repositories.coach_repository import CoachRepository
from app.repositories.school_repository import SchoolRepository
from app.models import CoachProfile
from fastapi import HTTPException, status


class CoachService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CoachRepository(session)
        self.school_repo = SchoolRepository(session)

    async def get_coach(self, coach_id: int) -> Optional[CoachProfile]:
        return await self.repo.get_by_id(coach_id)

    async def get_coaches_by_school(self, school_id: int) -> List[CoachProfile]:
        return await self.repo.get_by_school(school_id)

    async def search_coaches(self, name: str = "", school_id: int = None) -> List[CoachProfile]:
        return await self.repo.search(name, school_id)

    async def create_coach_profile(
        self,
        user_id: int,
        school_id: int = None,
        qualification: str = None,
        experience_years: int = 0,
        specialization: str = None,
        is_head_coach: bool = False,
        bio: str = None,
        achievements: str = None,
        photo_url: str = None,
        birth_date: datetime = None,
    ) -> CoachProfile:
        # Проверяем, существует ли школа
        if school_id:
            school = await self.school_repo.get_by_id(school_id)
            if not school:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"School with id {school_id} not found"
                )
        
        return await self.repo.create(
            user_id=user_id,
            school_id=school_id,
            qualification=qualification,
            experience_years=experience_years,
            specialization=specialization,
            is_head_coach=is_head_coach,
            bio=bio,
            achievements=achievements,
            photo_url=photo_url,
            birth_date=birth_date,
        )

    async def get_coach_athletes(self, coach_id: int) -> List:
        """Получить всех учеников тренера"""
        from sqlalchemy import select
        from app.models import AthleteProfile, User
        
        result = await self.session.execute(
            select(AthleteProfile)
            .options(selectinload(AthleteProfile.user))
            .where(AthleteProfile.coach_id == coach_id)
        )
        return result.scalars().all()

    async def update_coach(self, coach_id: int, **kwargs) -> Optional[CoachProfile]:
        """Обновить данные тренера"""
        return await self.repo.update(coach_id, **kwargs)
```

---

### `app/services/competition_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.competition_repository import CompetitionRepository
from app.models import Competition


class CompetitionService:
    """Сервис для работы с соревнованиями"""

    def __init__(self, session: AsyncSession):
        self.repo = CompetitionRepository(session)

    async def create_competition(
        self,
        name: str,
        start_date,
        end_date,
        created_by: int,
        description: Optional[str] = None,
        venue: Optional[str] = None,
        city: Optional[str] = None,
        status: str = "draft",
        max_participants: int = 0,
    ) -> Competition:
        """Создать новое соревнование"""
        competition = await self.repo.create(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            city=city,
            status=status,
            max_participants=max_participants,
            created_by=created_by,
        )
        return competition

    async def get_competition(self, competition_id: int) -> Optional[Competition]:
        """Получить соревнование по ID"""
        return await self.repo.get_by_id(competition_id)

    async def get_all_competitions(
        self, skip: int = 0, limit: int = 100
    ) -> List[Competition]:
        """Получить список всех соревнований"""
        return await self.repo.get_all(skip, limit)

    async def update_competition(
        self, competition_id: int, **kwargs
    ) -> Optional[Competition]:
        """Обновить соревнование"""
        return await self.repo.update(competition_id, **kwargs)

    async def delete_competition(self, competition_id: int) -> bool:
        """Удалить соревнование"""
        return await self.repo.delete(competition_id)

    async def get_active_competitions(self) -> List[Competition]:
        """Получить активные соревнования"""
        return await self.repo.get_active()

    async def get_upcoming_competitions(self) -> List[Competition]:
        """Получить предстоящие соревнования"""
        return await self.repo.get_upcoming()

    async def search_competitions(
        self, name: str = "", city: str = "", status: str = "", page: int = 1
    ) -> dict:
        return await self.repo.search(name, city, status, page)
```

---

### `app/services/csv_service.py`

```python
import csv
from io import StringIO, BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime


class CSVService:
    
    @staticmethod
    async def export_competition_results(competition_id: int, db: AsyncSession) -> BytesIO:
        """Экспорт результатов соревнования в CSV"""
        
        # Получаем данные
        result = await db.execute(
            text("""
                SELECT 
                    c.name as competition_name,
                    se.name as event_name,
                    se.distance,
                    se.stroke,
                    a.gender,
                    u.full_name as athlete_name,
                    s.name as school_name,
                    he.result_time,
                    he.place,
                    h.heat_number,
                    he.lane
                FROM competitions c
                JOIN swim_events se ON se.competition_id = c.id
                JOIN entries e ON e.swim_event_id = se.id
                JOIN heat_entries he ON he.entry_id = e.id
                JOIN athlete_profiles a ON a.id = e.athlete_id
                JOIN "user" u ON u.id = a.user_id
                LEFT JOIN schools s ON s.id = a.school_id
                JOIN heats h ON h.id = he.heat_id
                WHERE c.id = :competition_id AND he.result_time IS NOT NULL
                ORDER BY se.order, he.place
            """),
            {"competition_id": competition_id}
        )
        
        rows = result.fetchall()
        
        # Создаем CSV в памяти
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Заголовки
        writer.writerow([
            'Соревнование', 'Дистанция', 'Стиль', 'Пол',
            'Спортсмен', 'Школа', 'Результат (сек)', 'Место',
            'Заплыв', 'Дорожка', 'Дата экспорта'
        ])
        
        # Данные
        for row in rows:
            writer.writerow([
                row.competition_name,
                f"{row.distance}м",
                row.stroke,
                row.gender or 'mixed',
                row.athlete_name,
                row.school_name or '-',
                row.result_time,
                row.place or '-',
                row.heat_number,
                row.lane,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Конвертируем в BytesIO для отправки
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return output_bytes
    
    @staticmethod
    async def export_athlete_results(athlete_id: int, db: AsyncSession) -> BytesIO:
        """Экспорт результатов конкретного спортсмена"""
        
        result = await db.execute(
            text("""
                SELECT 
                    c.name as competition_name,
                    c.start_date,
                    se.name as event_name,
                    se.distance,
                    se.stroke,
                    he.result_time,
                    he.place
                FROM athlete_profiles a
                JOIN entries e ON e.athlete_id = a.id
                JOIN swim_events se ON se.id = e.swim_event_id
                JOIN competitions c ON c.id = se.competition_id
                JOIN heat_entries he ON he.entry_id = e.id
                WHERE a.id = :athlete_id AND he.result_time IS NOT NULL
                ORDER BY c.start_date DESC
            """),
            {"athlete_id": athlete_id}
        )
        
        rows = result.fetchall()
        
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        writer.writerow([
            'Соревнование', 'Дата', 'Дистанция', 'Стиль', 
            'Результат (сек)', 'Место'
        ])
        
        for row in rows:
            writer.writerow([
                row.competition_name,
                row.start_date.strftime('%d.%m.%Y') if row.start_date else '-',
                f"{row.distance}м",
                row.stroke,
                row.result_time,
                row.place or '-'
            ])
        
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return output_bytes
```

---

### `app/services/entry_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from io import BytesIO
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from app.repositories.entry_repository import EntryRepository
from app.models import Entry
from app.core.exceptions import FileTooLargeError, InvalidFileError

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class EntryService:
    """Сервис для работы с заявками"""

    def __init__(self, session: AsyncSession):
        self.repo = EntryRepository(session)

    async def create_entry(
        self,
        competition_id: int,
        swim_event_id: int,
        athlete_id: int,
        entry_time: Optional[float] = None,
        status: str = "pending",
    ) -> Entry:
        """Создать новую заявку"""
        return await self.repo.create(
            competition_id=competition_id,
            swim_event_id=swim_event_id,
            athlete_id=athlete_id,
            entry_time=entry_time,
            status=status,
        )

    async def get_entry(self, entry_id: int) -> Optional[Entry]:
        """Получить заявку по ID"""
        return await self.repo.get_by_id(entry_id)

    async def get_entries_by_competition(self, competition_id: int) -> List[Entry]:
        """Получить все заявки для соревнования"""
        return await self.repo.get_by_competition(competition_id)

    async def get_entries_by_swim_event(self, swim_event_id: int) -> List[Entry]:
        """Получить заявки для дистанции"""
        return await self.repo.get_by_swim_event(swim_event_id)

    async def get_entries_by_athlete(self, athlete_id: int) -> List[Entry]:
        """Получить заявки спортсмена"""
        return await self.repo.get_by_athlete(athlete_id)

    async def update_entry_status(self, entry_id: int, status: str) -> Optional[Entry]:
        """Обновить статус заявки"""
        return await self.repo.update_status(entry_id, status)

    async def delete_entry(self, entry_id: int) -> bool:
        """Удалить заявку"""
        return await self.repo.delete(entry_id)

    async def import_from_excel(self, competition_id: int, file_content: bytes) -> dict:
        """Импорт заявок из Excel файла"""

        # Проверка размера файла
        if len(file_content) > MAX_FILE_SIZE:
            raise FileTooLargeError("File too large (max 5MB)")

        try:
            wb = load_workbook(BytesIO(file_content), read_only=True, data_only=True)
            ws = wb.active
        except Exception as e:
            raise InvalidFileError(f"Error reading Excel file: {str(e)}")

        entries_data = []
        errors = []

        for row_idx, row in enumerate(
            ws.iter_rows(min_row=2, values_only=True), start=2
        ):
            try:
                swim_event_id = row[0]
                athlete_id = row[1]
                entry_time = row[2]
                status = row[3] if len(row) > 3 else "pending"

                if not swim_event_id or not athlete_id:
                    continue

                swim_event_id = int(swim_event_id)
                athlete_id = int(athlete_id)
                entry_time = float(entry_time) if entry_time else None

                if status not in ["pending", "confirmed", "rejected", "scratched"]:
                    status = "pending"

                entry = await self.create_entry(
                    competition_id=competition_id,
                    swim_event_id=swim_event_id,
                    athlete_id=athlete_id,
                    entry_time=entry_time,
                    status=status,
                )
                entries_data.append(entry)
            except (ValueError, TypeError) as e:
                errors.append(f"Row {row_idx}: Invalid data - {str(e)}")
                continue  # Продолжаем со следующей строкой
            except Exception as e:
                errors.append(f"Row {row_idx}: Database error - {str(e)}")
                continue  # Продолжаем со следующей строкой

        return {
            "message": f"Successfully created {len(entries_data)} entries",
            "entries": entries_data,
            "errors": errors if errors else None,
        }

    async def generate_excel_template(self, competition_id: int) -> BytesIO:
        """Генерация Excel шаблона для заявок"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Заявки"

        headers = ["swim_event_id", "athlete_id", "entry_time (сек)", "status"]

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(
            start_color="366092", end_color="366092", fill_type="solid"
        )

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        ws.cell(row=2, column=1, value="1")
        ws.cell(row=2, column=2, value="1")
        ws.cell(row=2, column=3, value="30.5")
        ws.cell(row=2, column=4, value="pending")

        ws.column_dimensions["A"].width = 15
        ws.column_dimensions["B"].width = 15
        ws.column_dimensions["C"].width = 20
        ws.column_dimensions["D"].width = 15

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
```

---

### `app/services/heat_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Dict, Any
from app.repositories.entry_repository import EntryRepository
from app.repositories.heat_repository import HeatRepository, HeatEntryRepository
from app.models import Entry, Heat, HeatEntry, AthleteProfile, AgeCategory, SwimEvent


class HeatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.heat_repo = HeatRepository(session)
        self.heat_entry_repo = HeatEntryRepository(session)

    async def generate_heats(self, swim_event_id: int) -> Dict[str, Any]:
        """Генерация заплывов для дистанции"""

        # 1. Получаем swim_event
        result = await self.session.execute(
            select(SwimEvent).where(SwimEvent.id == swim_event_id)
        )
        swim_event = result.scalar_one_or_none()
        if not swim_event:
            return {"message": "Swim event not found"}

        # 2. Получаем все заявки для дистанции с предварительной загрузкой связанных данных
        result = await self.session.execute(
            select(Entry)
            .where(Entry.swim_event_id == swim_event_id)
            .options(selectinload(Entry.athlete), selectinload(Entry.competition))
        )
        entries = result.scalars().all()

        if not entries:
            return {"message": "No entries for this swim event"}

        # 3. Получаем возрастные категории для соревнования
        competition_id = entries[0].competition_id
        result = await self.session.execute(
            select(AgeCategory).where(AgeCategory.competition_id == competition_id)
        )
        age_categories = result.scalars().all()

        # 4. Группируем по категориям
        groups = {}
        for entry in entries:
            athlete = entry.athlete
            if not athlete or not athlete.birth_date:
                continue

            # Расчёт возраста
            age = self._calculate_age(athlete.birth_date)

            # Поиск подходящей возрастной категории
            age_category = None
            for cat in age_categories:
                if cat.min_age <= age <= cat.max_age:
                    if cat.gender is None or cat.gender == athlete.gender:
                        age_category = cat
                        break

            if not age_category:
                continue

            # Ключ группы
            group_key = f"{age_category.id}_{athlete.gender or 'mixed'}_{swim_event.distance}_{swim_event.stroke}"

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(entry)

        # 5. Для каждой группы создаём заплывы
        heats_created = []
        for group_key, group_entries in groups.items():
            # Сортируем по личному рекорду
            group_entries.sort(key=lambda e: e.entry_time or float("inf"))

            # Разбиваем на заплывы по 8 человек
            lane_count = 8
            for i in range(0, len(group_entries), lane_count):
                heat_entries = group_entries[i : i + lane_count]

                # Создаём заплыв
                heat = Heat(
                    swim_event_id=swim_event_id,
                    heat_number=len(heats_created) + 1,
                    lane_count=lane_count,
                    status="scheduled",
                )
                self.session.add(heat)
                await self.session.flush()

                # Расставляем по дорожкам (алгоритм FINA)
                lane_order = self._get_lane_order(len(heat_entries))

                for idx, entry in enumerate(heat_entries):
                    lane = lane_order[idx] if idx < len(lane_order) else None
                    if lane:
                        heat_entry = HeatEntry(
                            heat_id=heat.id, entry_id=entry.id, lane=lane
                        )
                        self.session.add(heat_entry)

                heats_created.append(heat)

        await self.session.commit()

        return {
            "message": f"Created {len(heats_created)} heats",
            "heats_count": len(heats_created),
        }

    def _calculate_age(self, birth_date) -> int:
        """Расчёт возраста"""
        from datetime import datetime, timezone

        today = datetime.now(timezone.utc)
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    def _get_lane_order(self, num_entries: int) -> List[int]:
        """Алгоритм FINA для расстановки по дорожкам"""
        center_lanes = [4, 5, 3, 6, 2, 7, 1, 8]
        return center_lanes[:num_entries]

    async def get_heats_by_swim_event(self, swim_event_id: int) -> List[Heat]:
        """Получить все заплывы для дистанции"""
        return await self.heat_repo.get_by_swim_event(swim_event_id)

    async def enter_result(self, heat_entry_id: int, result_time: float) -> HeatEntry:
        """Ввод результата для участника"""
        heat_entry = await self.heat_entry_repo.get_by_id(heat_entry_id)
        if not heat_entry:
            raise ValueError("Heat entry not found")

        # Обновляем результат
        heat_entry.result_time = result_time
        await self.heat_entry_repo.update(heat_entry_id, result_time=result_time)

        return heat_entry

    async def complete_heat(self, heat_id: int) -> Heat:
        """Завершить заплыв и рассчитать места"""
        heat = await self.heat_repo.get_by_id(heat_id)
        if not heat:
            raise ValueError("Heat not found")

        # Получаем все результаты заплыва
        entries = await self.heat_entry_repo.get_by_heat(heat_id)

        # Сортируем по времени (лучшее время - первое место)
        entries_sorted = sorted(
            [e for e in entries if e.result_time is not None],
            key=lambda e: e.result_time,
        )

        # Назначаем места
        for i, entry in enumerate(entries_sorted):
            entry.place = i + 1
            await self.heat_entry_repo.update(entry.id, place=entry.place)

        # Обновляем статус заплыва
        heat.status = "completed"
        heat.completed_at = datetime.now(timezone.utc)
        await self.heat_repo.update(
            heat_id, status="completed", completed_at=heat.completed_at
        )

        return heat

    async def get_heat_results(self, heat_id: int):
        """Получить результаты заплыва"""
        return await self.heat_entry_repo.get_by_heat(heat_id)

    async def get_live_results(self, competition_id: int) -> List[dict]:
        """Получить актуальные результаты для live-таблицы"""

        # Получаем все завершённые заплывы для соревнования
        from sqlalchemy.orm import selectinload

        result = await self.session.execute(
            select(Heat)
            .options(
                selectinload(Heat.entries)
                .selectinload(HeatEntry.entry)
                .selectinload(Entry.athlete)
                .selectinload(AthleteProfile.user)
            )
            .join(SwimEvent)
            .where(
                SwimEvent.competition_id == competition_id, Heat.status == "completed"
            )
        )
        heats = result.scalars().all()

        live_data = []
        for heat in heats:
            for heat_entry in heat.entries:
                athlete = heat_entry.entry.athlete
                user = athlete.user if athlete else None

                live_data.append(
                    {
                        "heat_number": heat.heat_number,
                        "lane": heat_entry.lane,
                        "athlete_name": (
                            user.full_name
                            if user
                            else f"Athlete {heat_entry.entry.athlete_id}"
                        ),
                        "result_time": heat_entry.result_time,
                        "place": heat_entry.place,
                    }
                )

        print(f"DEBUG: Found {len(live_data)} results")  # Временная отладка
        return live_data
```

---

### `app/services/image_service.py`

```python
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import shutil

class ImageService:
    UPLOAD_DIR = Path("app/static/uploads")
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_SIZE = 5 * 1024 * 1024
    
    @classmethod
    async def save_image(cls, file: UploadFile, folder: str, resize: Optional[tuple[int, int]] = None) -> str:
        upload_path = cls.UPLOAD_DIR / folder
        upload_path.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Неподдерживаемый формат")
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > cls.MAX_SIZE:
            raise HTTPException(400, f"Файл слишком большой")
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_path / unique_name
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if resize:
            cls.resize_image(file_path, resize)
        return f"/static/uploads/{folder}/{unique_name}"
    
    @classmethod
    def resize_image(cls, path: Path, size: tuple[int, int]):
        try:
            img = Image.open(path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(path, optimize=True, quality=85)
        except Exception as e:
            print(f"Error: {e}")
```

---

### `app/services/news_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.news_repository import NewsRepository
from app.models import News


class NewsService:
    def __init__(self, session: AsyncSession):
        self.repo = NewsRepository(session)

    async def create_news(self, title: str, content: str, author_id: int) -> News:
        return await self.repo.create(title=title, content=content, author_id=author_id)

    async def publish_news(self, news_id: int) -> Optional[News]:
        from datetime import datetime, timezone

        return await self.repo.update(
            news_id, is_published=True, published_at=datetime.now(timezone.utc)
        )

    async def get_news(self, news_id: int) -> Optional[News]:
        return await self.repo.get_by_id(news_id)

    async def get_all_published(self, skip: int = 0, limit: int = 100) -> List[News]:
        return await self.repo.get_published(skip, limit)

    async def update_news(self, news_id: int, **kwargs) -> Optional[News]:
        return await self.repo.update(news_id, **kwargs)

    async def delete_news(self, news_id: int) -> bool:
        return await self.repo.delete(news_id)

    async def search_news(
        self, query: str = "", sort: str = "newest", page: int = 1
    ) -> dict:
        return await self.repo.search(query, sort, page)
```

---

### `app/services/pdf_service.py`

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime
from app.models import Competition, Heat, HeatEntry


class PDFService:
    @staticmethod
    async def generate_start_list(competition_id: int, session) -> BytesIO:
        """Генерация предстартового протокола"""
        # Получаем данные
        result = await session.execute(
            select(Heat)
            .where(Heat.competition_id == competition_id)
            .order_by(Heat.heat_number)
        )
        heats = result.scalars().all()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
        )
        styles = getSampleStyleSheet()
        elements = []

        # Заголовок
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,  # Center
            spaceAfter=30,
        )
        elements.append(Paragraph("Предстартовый протокол", title_style))
        elements.append(Spacer(1, 20))

        # Данные для каждого заплыва
        for heat in heats:
            heat_style = ParagraphStyle(
                "HeatTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=10
            )
            elements.append(Paragraph(f"Заплыв №{heat.heat_number}", heat_style))

            # Получаем участников
            entries_result = await session.execute(
                select(HeatEntry)
                .where(HeatEntry.heat_id == heat.id)
                .order_by(HeatEntry.lane)
            )
            entries = entries_result.scalars().all()

            # Таблица
            data = [["Дорожка", "Спортсмен", "Время"]]
            for entry in entries:
                athlete_name = (
                    entry.entry.athlete.user.full_name if entry.entry.athlete else "N/A"
                )
                data.append(
                    [str(entry.lane), athlete_name, entry.entry.entry_time or "-"]
                )

            table = Table(data, colWidths=[3 * cm, 8 * cm, 4 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    async def generate_results_protocol(competition_id: int, session) -> BytesIO:
        """Генерация итогового протокола"""
        # Получаем завершённые заплывы
        result = await session.execute(
            select(Heat)
            .where(Heat.competition_id == competition_id, Heat.status == "completed")
            .order_by(Heat.heat_number)
        )
        heats = result.scalars().all()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
        )
        styles = getSampleStyleSheet()
        elements = []

        # Заголовок
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,
            spaceAfter=30,
        )
        elements.append(Paragraph("Итоговый протокол соревнований", title_style))
        elements.append(Spacer(1, 20))

        for heat in heats:
            heat_style = ParagraphStyle(
                "HeatTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=10
            )
            elements.append(
                Paragraph(f"Заплыв №{heat.heat_number} (результаты)", heat_style)
            )

            entries_result = await session.execute(
                select(HeatEntry)
                .where(HeatEntry.heat_id == heat.id)
                .order_by(HeatEntry.place)
            )
            entries = entries_result.scalars().all()

            data = [["Место", "Дорожка", "Спортсмен", "Результат"]]
            for entry in entries:
                athlete_name = (
                    entry.entry.athlete.user.full_name if entry.entry.athlete else "N/A"
                )
                result_time = f"{entry.result_time:.2f}" if entry.result_time else "-"
                data.append(
                    [
                        str(entry.place or "-"),
                        str(entry.lane),
                        athlete_name,
                        result_time,
                    ]
                )

            table = Table(data, colWidths=[2 * cm, 2.5 * cm, 8 * cm, 3 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer
```

---

### `app/services/school_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.repositories.school_repository import SchoolRepository
from app.models import School


class SchoolService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SchoolRepository(session)

    async def create_school(
        self,
        name: str,
        city: str,
        address: str,
        description: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        website: Optional[str] = None,
        logo_url: Optional[str] = None,
        cover_url: Optional[str] = None,
        founded_year: Optional[int] = None,
    ) -> School:
        return await self.repo.create(
            name=name,
            city=city,
            address=address,
            description=description,
            phone=phone,
            email=email,
            website=website,
            logo_url=logo_url,
            cover_url=cover_url,
            founded_year=founded_year,
        )

    async def get_school(self, school_id: int) -> Optional[School]:
        result = await self.session.execute(
            select(School).where(School.id == school_id)
        )
        return result.scalar_one_or_none()

    async def get_all_schools(self, skip: int = 0, limit: int = 100) -> List[School]:
        result = await self.session.execute(
            select(School).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def search_schools(self, name: str = "", city: str = "", page: int = 1) -> dict:
        return await self.repo.search(name, city, page)

    async def update_school(self, school_id: int, **kwargs) -> Optional[School]:
        return await self.repo.update(school_id, **kwargs)

    async def delete_school(self, school_id: int) -> bool:
        return await self.repo.delete(school_id)

    async def create_branch(self, school_id: int, name: str, address: str, phone: str = None):
        from app.models import Branch
        branch = Branch(school_id=school_id, name=name, address=address, phone=phone)
        self.session.add(branch)
        await self.session.commit()
        await self.session.refresh(branch)
        return branch

    async def get_branches(self, school_id: int):
        from app.models import Branch
        from sqlalchemy import select
        result = await self.session.execute(select(Branch).where(Branch.school_id == school_id))
        return result.scalars().all()
```

---

### `app/services/swim_event_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.swim_event_repository import SwimEventRepository
from app.models import SwimEvent


class SwimEventService:
    def __init__(self, session: AsyncSession):
        self.repo = SwimEventRepository(session)

    async def create_swim_event(
        self,
        competition_id: int,
        name: str,
        distance: int,
        stroke: str,
        gender: Optional[str] = None,
        is_relay: bool = False,
        order: int = 0,
    ) -> SwimEvent:
        return await self.repo.create(
            competition_id=competition_id,
            name=name,
            distance=distance,
            stroke=stroke,
            gender=gender,
            is_relay=is_relay,
            order=order,
        )

    async def get_by_competition(self, competition_id: int) -> List[SwimEvent]:
        return await self.repo.get_by_competition(competition_id)

    async def get_swim_event(self, event_id: int) -> Optional[SwimEvent]:
        return await self.repo.get_by_id(event_id)

    async def update_swim_event(self, event_id: int, **kwargs) -> Optional[SwimEvent]:
        return await self.repo.update(event_id, **kwargs)

    async def delete_swim_event(self, event_id: int) -> bool:
        return await self.repo.delete(event_id)
```

---

### `app/static/css/style.css`

```css
/* Собственные стили для плавательного портала */

/* Карточки с тенью при наведении */
.card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

/* Анимация для кнопок */
.btn {
    transition: all 0.2s ease;
}

.btn:hover {
    transform: translateY(-2px);
}

/* Футер прижат к низу */
body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

main {
    flex: 1;
}
```

---

### `app/static/js/auth.js`

```javascript
// Хранение токена
let accessToken = null;

// Функция логина
async function login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch('/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
        credentials: 'include'
    });
    
    const data = await response.json();
    
    if (response.ok) {
        accessToken = data.access_token;
        // Сохраняем в localStorage
        localStorage.setItem('access_token', accessToken);
        return true;
    }
    return false;
}

// Функция получения заголовков с токеном
function authHeaders() {
    const token = accessToken || localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Функция авторизованных запросов
async function authFetch(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...authHeaders(),
        ...options.headers
    };
    
    return fetch(url, {
        ...options,
        headers,
        credentials: 'include'
    });
}
```

---

### `app/static/js/toast.js`

```javascript
// Глобальная функция для показа уведомлений
window.showToast = function(message, type = 'success') {
    // Находим или создаем контейнер для тостов
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Определяем цвет и иконку в зависимости от типа
    const config = {
        success: { bg: 'bg-success', icon: 'fa-check-circle' },
        error: { bg: 'bg-danger', icon: 'fa-exclamation-circle' },
        warning: { bg: 'bg-warning', icon: 'fa-exclamation-triangle' },
        info: { bg: 'bg-info', icon: 'fa-info-circle' }
    };
    
    const cfg = config[type] || config.success;
    
    // Создаем тост
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${cfg.bg} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="3000">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${cfg.icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    // Удаляем элемент после скрытия
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
};

// Успешное уведомление
window.showSuccess = function(message) {
    window.showToast(message, 'success');
};

// Ошибка
window.showError = function(message) {
    window.showToast(message, 'error');
};

// Предупреждение
window.showWarning = function(message) {
    window.showToast(message, 'warning');
};

// Информация
window.showInfo = function(message) {
    window.showToast(message, 'info');
};

console.log('✅ Toast notifications loaded');
```

---

### `app/templates/athlete_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-body">
                {% if athlete.photo_url %}
                <img src="{{ athlete.photo_url }}" class="rounded-circle mb-3" style="width: 150px; height: 150px; object-fit: cover;">
                {% else %}
                <div class="rounded-circle bg-secondary mx-auto d-flex align-items-center justify-content-center mb-3" style="width: 150px; height: 150px;">
                    <i class="fas fa-user fa-5x text-white"></i>
                </div>
                {% endif %}
                <h3>{{ athlete.user.full_name }}</h3>
                <p class="text-muted">
                    <i class="fas fa-tag"></i> Спортсмен
                    {% if athlete.rank %}
                    <span class="badge bg-success ms-2">{{ athlete.rank }}</span>
                    {% endif %}
                </p>
                
                {% if school %}
                <p class="mt-3">
                    <i class="fas fa-school"></i> 
                    <a href="/schools/{{ school.id }}/page">{{ school.name }}</a>
                </p>
                {% endif %}
                
                {% if coach %}
                <p>
                    <i class="fas fa-chalkboard-user"></i> 
                    <a href="/coaches/{{ coach.id }}/page">Тренер: {{ coach.user.full_name }}</a>
                </p>
                <p><small class="text-muted">Стаж тренера: {{ coach.experience_years }} лет</small></p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-8">
        <div class="card mb-4">
            <div class="card-body">
                <h4 class="card-title">О спортсмене</h4>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <p><strong><i class="fas fa-calendar"></i> Дата рождения:</strong><br>
                        {% if athlete.birth_date %}
                        {{ athlete.birth_date.strftime('%d.%m.%Y') }} ({{ (now.year - athlete.birth_date.year) }} лет)
                        {% else %}
                        Не указана
                        {% endif %}
                        </p>
                    </div>
                    <div class="col-md-6">
                        <p><strong><i class="fas fa-venus-mars"></i> Пол:</strong><br>
                        {{ athlete.gender or 'Не указан' }}
                        </p>
                    </div>
                </div>
                
                <div class="mb-4">
                    <p><strong><i class="fas fa-medal"></i> Разряд:</strong><br>
                    {{ athlete.rank or 'Не указан' }}
                    </p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Личные рекорды</h4>
                
                {% if personal_bests %}
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Дистанция</th>
                                <th>Стиль</th>
                                <th>Время (сек)</th>
                                <th>Дата установки</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for key, pb in personal_bests.items() %}
                            <tr>
                                <td>{{ pb.distance }} м</td>
                                <td>{{ pb.stroke }}</td>
                                <td><strong>{{ pb.time_seconds }}</strong></td>
                                <td>{{ pb.set_at.strftime('%d.%m.%Y') if pb.set_at else '-' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">Личные рекорды не добавлены</p>
                {% endif %}
            </div>
        </div>
        
        <div class="text-center mt-3">
            <a href="javascript:history.back()" class="btn btn-secondary">← Назад</a>
        </div>
    </div>
</div>
{% endblock %}
```

---

### `app/templates/base.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Плавательный портал</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-swimmer"></i> Плавательный портал</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/news/page">Новости</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/schools/page">Школы</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/competitions/page">Соревнования</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/articles/page">Обучение</a>
                    </li>
                    <li class="nav-item"><a class="nav-link" href="/">Главная</a></li>
                    <li class="nav-item"><a class="nav-link" href="/live"><i class="fas fa-chart-line"></i> Live</a></li>
                    <li class="nav-item"><a class="nav-link" href="/login">Вход</a></li>
                    <li class="nav-item"><a class="nav-link" href="/register">Регистрация</a></li>
                    <li class="nav-item"><a class="nav-link" href="/profile">Профиль</a></li>
                    <li class="nav-item"><a class="nav-link" href="/coach/dashboard"><i class="fas fa-chalkboard-user"></i> Мои ученики</a></li>
                </ul>
            </div>
        </div>
    </nav>
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Toast Notifications -->
    <script src="/static/js/toast.js"></script>
    
    <!-- Global confirmation modal -->
    <div x-data="{ showModal: false, modalMessage: '', modalAction: null }" 
         x-init="window.showConfirm = (msg, callback) => { modalMessage = msg; modalAction = callback; showModal = true; }">
        <div x-show="showModal" 
             class="modal fade show" 
             style="display: block; background-color: rgba(0,0,0,0.5); position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9999;"
             @click.away="showModal = false">
            <div class="modal-dialog modal-dialog-centered" style="margin-top: 20%;">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">Подтверждение действия</h5>
                        <button type="button" class="btn-close btn-close-white" @click="showModal = false"></button>
                    </div>
                    <div class="modal-body">
                        <p x-text="modalMessage"></p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="showModal = false">Отмена</button>
                        <button type="button" class="btn btn-danger" @click="modalAction(); showModal = false">Подтвердить</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function getToken() {
        const match = document.cookie.match(/access_token=([^;]+)/);
        return match ? match[1] : null;
    }
    
    // Проверяем, что уведомления загружены
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof window.showSuccess === 'function') {
            console.log('✅ Toast notifications ready');
        } else {
            console.warn('⚠️ Toast notifications not loaded');
        }
    });
    </script>
</body>
</html>
```

---

### `app/templates/branch_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/schools/{{ school.id }}/page">{{ school.name }}</a></li>
                <li class="breadcrumb-item active" aria-current="page">{{ branch.name }}</li>
            </ol>
        </nav>
        
        <!-- Информация о филиале -->
        <div class="card mb-4">
            <div class="card-header">
                <h3>{{ branch.name }}</h3>
            </div>
            <div class="card-body">
                <p><strong>Адрес:</strong> {{ branch.address }}</p>
                {% if branch.phone %}
                <p><strong>Телефон:</strong> {{ branch.phone }}</p>
                {% endif %}
                <p><strong>Школа:</strong> <a href="/schools/{{ school.id }}/page">{{ school.name }}</a></p>
            </div>
        </div>
        
        <!-- Старший тренер филиала -->
        <div id="head-coach-section" class="mb-4"></div>
        
        <!-- Остальные тренеры -->
        <div id="coaches-section"></div>
    </div>
</div>

<script>
async function loadBranchCoaches() {
    try {
        const response = await fetch('/branches/{{ branch.id }}/coaches');
        const coaches = await response.json();
        
        // Отделяем старшего тренера
        const headCoach = coaches.find(c => c.is_head_coach === true);
        const otherCoaches = coaches.filter(c => c.is_head_coach !== true);
        
        // Старший тренер
        const headCoachSection = document.getElementById('head-coach-section');
        if (headCoach) {
            headCoachSection.innerHTML = `
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">Старший тренер филиала</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-flex align-items-start">
                            <div class="flex-shrink-0 me-3">
                                ${headCoach.photo_url ? 
                                    `<img src="${headCoach.photo_url}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%;">` : 
                                    `<i class="fas fa-user-circle fa-4x text-secondary"></i>`
                                }
                            </div>
                            <div>
                                <h4>${headCoach.full_name}</h4>
                                <p><strong>Квалификация:</strong> ${headCoach.qualification || 'Не указана'}</p>
                                <p><strong>Стаж:</strong> ${headCoach.experience_years || 0} лет</p>
                                <p><strong>Специализация:</strong> ${headCoach.specialization || 'Не указана'}</p>
                                <a href="/coaches/${headCoach.id}/page" class="btn btn-outline-success btn-sm">Профиль тренера</a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            headCoachSection.innerHTML = `
                <div class="alert alert-info">
                    В этом филиале пока нет старшего тренера
                </div>
            `;
        }
        
        // Остальные тренеры
        const coachesSection = document.getElementById('coaches-section');
        if (otherCoaches.length > 0) {
            let coachesHtml = `
                <div class="card">
                    <div class="card-header">
                        <h5>Тренерский состав филиала (${otherCoaches.length})</h5>
                    </div>
                    <div class="list-group list-group-flush">
            `;
            otherCoaches.forEach(coach => {
                coachesHtml += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${coach.full_name}</strong>
                                <br>
                                <small class="text-muted">
                                    ${coach.qualification || 'Квалификация не указана'} | 
                                    Стаж: ${coach.experience_years || 0} лет | 
                                    Специализация: ${coach.specialization || 'не указана'}
                                </small>
                            </div>
                            <a href="/coaches/${coach.id}/page" class="btn btn-sm btn-outline-primary">Профиль</a>
                        </div>
                    </div>
                `;
            });
            coachesHtml += `</div></div>`;
            coachesSection.innerHTML = coachesHtml;
        } else {
            coachesSection.innerHTML = `
                <div class="alert alert-secondary">
                    В этом филиале пока нет других тренеров
                </div>
            `;
        }
    } catch (error) {
        console.error('Ошибка загрузки тренеров:', error);
        document.getElementById('head-coach-section').innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных</div>';
    }
}

loadBranchCoaches();
</script>
{% endblock %}
```

---

### `app/templates/coach_dashboard.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">
            <i class="fas fa-chalkboard-user text-primary"></i>
            Панель тренера
        </h1>
        
        <!-- Статистика -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h5 class="card-title">Ученики</h5>
                        <h2 class="mb-0">{{ stats.total_students or 0 }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h5 class="card-title">Соревнования</h5>
                        <h2 class="mb-0">{{ stats.total_competitions or 0 }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h5 class="card-title">Заплывы</h5>
                        <h2 class="mb-0">{{ stats.total_races or 0 }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <h5 class="card-title">Среднее место</h5>
                        <h2 class="mb-0">{{ "%.1f"|format(stats.avg_place or 0) }}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Список учеников -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Мои ученики</h5>
            </div>
            <div class="card-body">
                {% if students %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Email</th>
                                <th>Возраст</th>
                                <th>Разряд</th>
                                <th>Заплывов</th>
                                <th>Лучшее время</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for student in students %}
                            <tr>
                                <td>{{ student.full_name }}</td>
                                <td>{{ student.email }}</td>
                                <td>
                                    {% if student.birth_date %}
                                    {{ ((now.year - student.birth_date.year)) }} лет
                                    {% else %}
                                    -
                                    {% endif %}
                                </td>
                                <td>{{ student.rank or '-' }}</td>
                                <td>{{ student.races_count }}</td>
                                <td>
                                    {% if student.best_time %}
                                    {{ "%.2f"|format(student.best_time) }} сек
                                    {% else %}
                                    -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="/coach/student/{{ student.id }}" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-chart-line"></i> Результаты
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted text-center">У вас пока нет учеников</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### `app/templates/coach_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-body">
                {% if coach.photo_url %}
                <img src="{{ coach.photo_url }}" class="rounded-circle mb-3" style="width: 150px; height: 150px; object-fit: cover;">
                {% else %}
                <div class="rounded-circle bg-secondary mx-auto d-flex align-items-center justify-content-center mb-3" style="width: 150px; height: 150px;">
                    <i class="fas fa-user fa-5x text-white"></i>
                </div>
                {% endif %}
                <h3>{{ coach.user.full_name }}</h3>
                {% if coach.is_head_coach %}
                <span class="badge bg-warning mb-3">Главный тренер</span>
                {% endif %}
                
                {% if school %}
                <p class="mt-3">
                    <i class="fas fa-school"></i> 
                    <a href="/schools/{{ school.id }}/page">{{ school.name }}</a>
                </p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-8">
        <div class="card mb-4">
            <div class="card-body">
                <h4 class="card-title">О тренере</h4>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <p><strong><i class="fas fa-calendar"></i> Возраст:</strong><br>
                        {% if coach.birth_date %}
                        {{ coach.birth_date.strftime('%d.%m.%Y') }} ({{ (now.year - coach.birth_date.year) }} лет)
                        {% else %}
                        Не указан
                        {% endif %}
                        </p>
                    </div>
                    <div class="col-md-6">
                        <p><strong><i class="fas fa-chalkboard-user"></i> Тренерский стаж:</strong><br>
                        {{ coach.experience_years }} лет
                        </p>
                    </div>
                </div>
                
                <div class="mb-4">
                    <p><strong><i class="fas fa-graduation-cap"></i> Квалификация:</strong><br>
                    {{ coach.qualification or 'Не указана' }}
                    </p>
                </div>
                
                <div class="mb-4">
                    <p><strong><i class="fas fa-tag"></i> Специализация:</strong><br>
                    {{ coach.specialization or 'Не указана' }}
                    </p>
                </div>
                
                <div class="mb-4">
                    <p><strong><i class="fas fa-trophy"></i> Достижения:</strong><br>
                    {{ coach.achievements or 'Не указаны' }}
                    </p>
                </div>
                
                <div class="mb-4">
                    <p><strong><i class="fas fa-align-left"></i> Биография:</strong><br>
                    {{ coach.bio or 'Не указана' }}
                    </p>
                </div>
            </div>
        </div>
        
        {% if athletes %}
        <div class="card">
            <div class="card-body">
                <h4 class="card-title">Ученики</h4>
                <div class="list-group">
                    {% for athlete in athletes %}
                    <a href="/athletes/{{ athlete.id }}/page" class="list-group-item list-group-item-action">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{{ athlete.user.full_name }}</strong>
                                {% if athlete.rank %}
                                <span class="badge bg-success ms-2">{{ athlete.rank }}</span>
                                {% endif %}
                                <br>
                                <small class="text-muted">{{ athlete.gender or 'Пол не указан' }}</small>
                            </div>
                            <i class="fas fa-chevron-right"></i>
                        </div>
                    </a>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}
        
        <div class="text-center mt-3">
            <a href="javascript:history.back()" class="btn btn-secondary">← Назад</a>
        </div>
    </div>
</div>
{% endblock %}
```

---

### `app/templates/coach_student_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>
                <i class="fas fa-user-graduate text-primary"></i>
                {{ student.full_name }}
            </h1>
            <a href="/coach/dashboard" class="btn btn-secondary">
                ← Назад к ученикам
            </a>
        </div>
        
        <!-- Информация об ученике -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Личная информация</h5>
                        <table class="table table-sm">
                            <tr>
                                <th>Email:</th>
                                <td>{{ student.email }}</td>
                            </tr>
                            <tr>
                                <th>Дата рождения:</th>
                                <td>{{ student.birth_date.strftime('%d.%m.%Y') if student.birth_date else '-' }}</td>
                            </tr>
                            <tr>
                                <th>Пол:</th>
                                <td>{{ student.gender or '-' }}</td>
                            </tr>
                            <tr>
                                <th>Разряд:</th>
                                <td>{{ student.rank or '-' }}</td>
                            </tr>
                            <tr>
                                <th>Школа:</th>
                                <td>{{ student.school_name or '-' }}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Результаты -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Результаты выступлений</h5>
            </div>
            <div class="card-body">
                {% if results %}
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Соревнование</th>
                                <th>Дата</th>
                                <th>Дистанция</th>
                                <th>Стиль</th>
                                <th>Результат</th>
                                <th>Место</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for result in results %}
                            <tr>
                                <td>{{ result.competition_name }}</td>
                                <td>{{ result.start_date.strftime('%d.%m.%Y') if result.start_date else '-' }}</td>
                                <td>{{ result.distance }}м</td>
                                <td>{{ result.stroke }}</td>
                                <td><strong>{{ "%.2f"|format(result.result_time) }} сек</strong></td>
                                <td>
                                    {% if result.place == 1 %}🥇 1
                                    {% elif result.place == 2 %}🥈 2
                                    {% elif result.place == 3 %}🥉 3
                                    {% else %}{{ result.place or '-' }}
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted text-center">Нет результатов</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### `app/templates/competition_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <h1>{{ competition.name }}</h1>
                <p class="text-muted">{{ competition.description or 'Нет описания' }}</p>
                <hr>
                <p><strong>📅 Дата начала:</strong> {{ competition.start_date }}</p>
                <p><strong>📅 Дата окончания:</strong> {{ competition.end_date }}</p>
                <p><strong>📍 Место:</strong> {{ competition.venue or 'Не указано' }}, {{ competition.city or 'Не указан' }}</p>
                <p><strong>📊 Статус:</strong> <span class="badge bg-secondary">{{ competition.status }}</span></p>
                
                <div class="mt-3">
                    <a href="/competitions/{{ competition.id }}/start-list.pdf" class="btn btn-info">
                        <i class="fas fa-file-pdf"></i> Предстартовый протокол
                    </a>
                    <a href="/competitions/{{ competition.id }}/results.pdf" class="btn btn-success">
                        <i class="fas fa-file-pdf"></i> Итоговый протокол</a>
                    <a href="/competitions/{{ competition.id }}/results.csv" class="btn btn-info">
                        <i class="fas fa-file-csv"></i> CSV результаты
                    </a>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div x-data="chatComponent('competition_{{ competition.id }}')" x-init="initWebSocket()" class="card">
            <div class="card-header bg-primary text-white">
                <i class="fas fa-comments"></i> Чат соревнования
            </div>
            <div class="card-body" style="height: 300px; overflow-y: auto;" x-ref="messagesContainer">
                <template x-for="(msg, idx) in messages" :key="idx">
                    <div class="mb-2">
                        <strong x-text="msg.user"></strong>:
                        <span x-text="msg.message"></span>
                        <small class="text-muted ms-2" x-text="msg.created_at ? new Date(msg.created_at).toLocaleTimeString() : ''"></small>
                    </div>
                </template>
                <div x-show="messages.length === 0" class="text-muted text-center">
                    Нет сообщений. Будьте первым!
                </div>
            </div>
            <div class="card-footer">
                <div class="input-group">
                    <input type="text" class="form-control" x-model="newMessage" @keyup.enter="sendMessage()" placeholder="Введите сообщение...">
                    <button class="btn btn-primary" @click="sendMessage()" :disabled="!newMessage.trim()">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function chatComponent(room) {
    return {
        room: room,
        messages: [],
        newMessage: '',
        ws: null,

        initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.room}`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'message' || data.type === 'history') {
                    this.messages.push(data);
                    this.$nextTick(() => {
                        const container = this.$refs.messagesContainer;
                        if (container) container.scrollTop = container.scrollHeight;
                    });
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(() => this.initWebSocket(), 3000);
            };
        },

        sendMessage() {
            if (this.newMessage.trim() && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ message: this.newMessage.trim() }));
                this.newMessage = '';
            }
        }
    }
}
</script>
{% endblock %}

<div class="mt-3">
    <button class="btn btn-danger" onclick="deleteCompetition({{ competition.id }})">
        <i class="fas fa-trash"></i> Удалить соревнование
    </button>
</div>

<script>
function getToken() {
    const match = document.cookie.match(/access_token=([^;]+)/);
    return match ? match[1] : null;
}

function deleteCompetition(competitionId) {
    if (confirm('Вы уверены, что хотите удалить это соревнование? Действие необратимо.')) {
        fetch(`/competitions/${competitionId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        }).then(response => {
            if (response.ok) {
                window.location.href = '/competitions/page';
            } else {
                alert('Ошибка при удалении');
            }
        }).catch(err => {
            console.error('Ошибка:', err);
            alert('Ошибка при удалении');
        });
    }
}
</script>
<script>
// Дополняем существующий chatComponent
function chatComponentWithNotifications(room) {
    const component = chatComponent(room);
    
    // Сохраняем оригинальный sendMessage
    const originalSend = component.sendMessage;
    
    // Переопределяем sendMessage с уведомлением
    component.sendMessage = function() {
        if (this.newMessage.trim() && this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = this.newMessage.trim();
            this.ws.send(JSON.stringify({ message: message }));
            showSuccess('✉️ Сообщение отправлено');
            this.newMessage = '';
        } else if (!this.connected) {
            showError('❌ Нет соединения с чатом');
        }
    };
    
    return component;
}
</script>
```

---

### `app/templates/competitions_list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="text-center mb-4">Соревнования</h1>
        
        <div class="card mb-4">
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-md-4">
                        <input type="text" class="form-control" id="nameSearch" placeholder="Название"
                               oninput="searchCompetitions()">
                    </div>
                    <div class="col-md-3">
                        <input type="text" class="form-control" id="citySearch" placeholder="Город"
                               oninput="searchCompetitions()">
                    </div>
                    <div class="col-md-3">
                        <select class="form-select" id="statusFilter" onchange="searchCompetitions()">
                            <option value="">Все статусы</option>
                            <option value="registration_open">Регистрация открыта</option>
                            <option value="ongoing">В процессе</option>
                            <option value="completed">Завершены</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-secondary w-100" onclick="resetFilters()">
                            <i class="fas fa-undo"></i> Сбросить
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="competitionsList">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function searchCompetitions() {
    const name = encodeURIComponent(document.getElementById('nameSearch').value);
    const city = encodeURIComponent(document.getElementById('citySearch').value);
    const status = encodeURIComponent(document.getElementById('statusFilter').value);
    
    fetch(`/competitions/search?name=${name}&city=${city}&status=${status}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('competitionsList').innerHTML = html;
        })
        .catch(error => {
            console.error('Ошибка поиска:', error);
        });
}

function resetFilters() {
    document.getElementById('nameSearch').value = '';
    document.getElementById('citySearch').value = '';
    document.getElementById('statusFilter').value = '';
    searchCompetitions();
}

// Загружаем список при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    searchCompetitions();
});
</script>
{% endblock %}
```

---

### `app/templates/emails/password_reset.html`

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .reset-link { background: #f8f9fa; padding: 10px; word-break: break-all; }
        .footer { background: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Сброс пароля</h1>
        </div>
        <div class="content">
            <p>Вы запросили сброс пароля.</p>
            <p>Нажмите на кнопку ниже, чтобы установить новый пароль:</p>
            <p><a href="{{ reset_link }}" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none;">Сбросить пароль</a></p>
            <p>Или скопируйте ссылку:</p>
            <div class="reset-link">{{ reset_link }}</div>
            <p>Ссылка действительна в течение 1 часа.</p>
            <p>Если вы не запрашивали сброс пароля, проигнорируйте это письмо.</p>
        </div>
        <div class="footer">
            <p>© 2024 Плавательный портал</p>
        </div>
    </div>
</body>
</html>
```

---

### `app/templates/emails/welcome.html`

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #0d6efd; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏊 Плавательный портал</h1>
        </div>
        <div class="content">
            <h2>Добро пожаловать, {{ username }}!</h2>
            <p>Вы успешно зарегистрировались в Плавательном портале.</p>
            <p>Теперь вы можете:</p>
            <ul>
                <li>Участвовать в соревнованиях</li>
                <li>Отслеживать свои результаты</li>
                <li>Общаться с тренерами и спортсменами</li>
            </ul>
            <p><a href="http://localhost:8000/login" style="background: #0d6efd; color: white; padding: 10px 20px; text-decoration: none;">Войти в аккаунт</a></p>
        </div>
        <div class="footer">
            <p>© 2024 Плавательный портал. Все права защищены.</p>
        </div>
    </div>
</body>
</html>
```

---

### `app/templates/index.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto text-center">
        <h1 class="display-4 mb-4">
            <i class="fas fa-swimmer text-primary"></i>
            Добро пожаловать!
        </h1>
        <p class="lead">Спортивный портал для управления соревнованиями по плаванию</p>

        <div class="row mt-5">
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-trophy fa-3x text-warning mb-3"></i>
                        <h5 class="card-title">Соревнования</h5>
                        <p class="card-text">Участвуйте в соревнованиях и показывайте лучшие результаты</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-line fa-3x text-success mb-3"></i>
                        <h5 class="card-title">Рейтинги</h5>
                        <p class="card-text">Следите за рейтингом и улучшайте свои показатели</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-3x text-info mb-3"></i>
                        <h5 class="card-title">Команда</h5>
                        <p class="card-text">Тренируйтесь вместе с командой и достигайте новых высот</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-5" id="auth-buttons">
            <a href="/login" class="btn btn-primary btn-lg me-2">Вход</a>
            <a href="/register" class="btn btn-outline-primary btn-lg">Регистрация</a>
        </div>
    </div>
</div>

<script>
// Проверяем авторизацию через запрос к /auth/me
fetch('/auth/me', {
    credentials: 'include'  // Отправляем cookie
})
.then(response => {
    if (response.ok) {
        // Пользователь авторизован
        const authButtons = document.getElementById('auth-buttons');
        if (authButtons) {
            authButtons.innerHTML = `
                <p class="text-success">Вы вошли в систему!</p>
                <a href="/profile" class="btn btn-primary">Личный кабинет</a>
                <button onclick="logout()" class="btn btn-danger ms-2">Выйти</button>
            `;
        }
    }
})
.catch(() => {
    // Ошибка — пользователь не авторизован, оставляем кнопки входа
});

function logout() {
    const csrfToken = document.cookie.match(/csrf_token=([^;]+)/)?.[1];
    fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'X-CSRF-Token': csrfToken || ''
        }
    })
    .then(() => {
        window.location.href = '/';
    })
    .catch(() => {
        window.location.href = '/';
    });
}

async function getCsrfToken() {
    const match = document.cookie.match(/csrf_token=([^;]+)/);
    return match ? match[1] : null;
}

// Пример отправки POST запроса с CSRF защитой
async function changePassword(newPassword) {
    const csrfToken = await getCsrfToken();
    const response = await fetch('/auth/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({ password: newPassword }),
        credentials: 'include'
    });
    return response.ok;
}
</script>
{% endblock %}
```

---

### `app/templates/live.html`

```html
{% extends "base.html" %}

{% block title %}Live-таблица результатов{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="text-center mb-4">
            <i class="fas fa-chart-line text-primary"></i>
            Live-таблица результатов
        </h1>
        
        <div class="card">
            <div class="card-body">
                <div x-data="liveTable()" x-init="initSSE()">
                    <div x-show="loading" class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Загрузка...</span>
                        </div>
                    </div>
                    
                    <div x-show="!loading && results.length === 0" class="alert alert-info">
                        Нет завершённых результатов
                    </div>
                    
                    <div x-show="!loading && results.length > 0">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>Заплыв</th>
                                        <th>Дорожка</th>
                                        <th>Спортсмен</th>
                                        <th>Результат (сек)</th>
                                        <th>Место</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template x-for="result in results" :key="result.lane">
                                        <tr>
                                            <td x-text="result.heat_number"></td>
                                            <td x-text="result.lane"></td>
                                            <td x-text="result.athlete_name"></td>
                                            <td>
                                                <span x-text="result.result_time" 
                                                      :class="{'text-success fw-bold': result.result_time}"></span>
                                            </td>
                                            <td>
                                                <span x-show="result.place === 1">🥇 1</span>
                                                <span x-show="result.place === 2">🥈 2</span>
                                                <span x-show="result.place === 3">🥉 3</span>
                                                <span x-show="result.place && result.place > 3" x-text="result.place"></span>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-3">
            <a href="/" class="btn btn-secondary">На главную</a>
        </div>
    </div>
</div>

<script>
function liveTable() {
    return {
        results: [],
        loading: true,
        eventSource: null,
        
        initSSE() {
            this.loading = true;
            this.eventSource = new EventSource('/heats/live/1/events');
            
            this.eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (Array.isArray(data)) {
                    this.results = data;
                } else if (data.error) {
                    console.error('SSE error:', data.error);
                }
                this.loading = false;
            };
            
            this.eventSource.onerror = () => {
                console.error('SSE connection error');
                this.eventSource.close();
                setTimeout(() => this.initSSE(), 5000);
            };
        }
    };
}
</script>
{% endblock %}
```

---

### `app/templates/login.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Вход в систему</h3>

                <form id="loginForm" @submit.prevent="login">
                    <div class="mb-3">
                        <label for="username" class="form-label">Имя пользователя</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>

                    <div class="mb-3">
                        <label for="password" class="form-label">Пароль</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>

                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary">Войти</button>
                        <a href="/register" class="btn btn-link">Нет аккаунта? Зарегистрироваться</a>
                    </div>

                    <div id="errorMessage" class="alert alert-danger mt-3" style="display: none;"></div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('errorMessage');
    
    errorDiv.style.display = 'none';
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // После успешного входа - перезагружаем страницу, чтобы cookie применились
            window.location.href = '/';
        } else {
            errorDiv.textContent = data.detail || 'Ошибка входа';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Ошибка сети';
        errorDiv.style.display = 'block';
    }
});
</script>
{% endblock %}
```

---

### `app/templates/news_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <div class="card">
            <div class="card-body">
                <h1>{{ news.title }}</h1>
                <p class="text-muted">
                    {{ news.published_at.strftime('%d.%m.%Y') if news.published_at else 'Черновик' }}
                </p>
                <hr>
                <div class="mt-3">
                    {{ news.content | safe }}
                </div>
                <div class="mt-4">
                    <a href="/news/page" class="btn btn-secondary">← Назад к новостям</a>
                    
                    {% if current_user and current_user.role == 'admin' %}
                    <button onclick="deleteNews({{ news.id }})" class="btn btn-danger float-end">
                        <i class="fas fa-trash"></i> Удалить
                    </button>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function deleteNews(newsId) {
    if (confirm('Удалить эту новость?')) {
        const token = document.cookie.match(/access_token=([^;]+)/)?.[1];
        fetch(`/news/${newsId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).then(() => {
            window.location.href = '/news/page';
        });
    }
}
</script>
{% endblock %}
```

---

### `app/templates/news_list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <h1 class="text-center mb-4">Новости плавания</h1>
        
        <!-- Поиск -->
        <div class="card mb-4">
            <div class="card-body">
                <div class="input-group">
                    <input type="text" 
                           class="form-control" 
                           id="searchInput" 
                           placeholder="Поиск новостей..."
                           value="{{ q or '' }}">
                    <button class="btn btn-primary" 
                            hx-get="/news/search"
                            hx-include="#searchInput"
                            hx-target="#newsList">
                        <i class="fas fa-search"></i> Поиск
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Список новостей -->
        <div id="newsList" hx-get="/news/search" hx-trigger="load" hx-target="#newsList">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### `app/templates/partials/article_items.html`

```html
{% for article in articles %}
<div class="card mb-3">
    <div class="card-body">
        <span class="badge bg-primary mb-2">{{ article.category }}</span>
        <h5 class="card-title">{{ article.title }}</h5>
        <p class="card-text">{{ article.summary or article.content[:150] }}...</p>
        <small class="text-muted">Просмотров: {{ article.views }}</small>
        <a href="/articles/{{ article.id }}" class="btn btn-sm btn-primary float-end">Читать</a>
    </div>
</div>
{% else %}
<div class="alert alert-info">Статей не найдено</div>
{% endfor %}
```

---

### `app/templates/partials/chat.html`

```html
<div x-data="chatComponent(room)" x-init="initWebSocket()" class="card mt-4">
    <div class="card-header bg-primary text-white">
        <i class="fas fa-comments"></i> Чат соревнования
    </div>
    <div class="card-body" style="height: 300px; overflow-y: auto;" x-ref="messagesContainer">
        <template x-for="msg in messages" :key="msg.created_at">
            <div class="mb-2">
                <strong x-text="msg.user"></strong>:
                <span x-text="msg.message"></span>
                <small class="text-muted ms-2" x-text="new Date(msg.created_at).toLocaleTimeString()"></small>
            </div>
        </template>
        <div x-show="messages.length === 0" class="text-muted text-center">
            Нет сообщений. Будьте первым!
        </div>
    </div>
    <div class="card-footer">
        <div class="input-group">
            <input type="text" class="form-control" x-model="newMessage" @keyup.enter="sendMessage()" placeholder="Введите сообщение...">
            <button class="btn btn-primary" @click="sendMessage()" :disabled="!newMessage.trim()">
                <i class="fas fa-paper-plane"></i> Отправить
            </button>
        </div>
    </div>
</div>

<script>
function chatComponent(room) {
    return {
        room: room,
        messages: [],
        newMessage: '',
        ws: null,
        reconnectAttempts: 0,

        initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.room}`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'message' || data.type === 'history') {
                    this.messages.push(data);
                    this.$nextTick(() => {
                        const container = this.$refs.messagesContainer;
                        container.scrollTop = container.scrollHeight;
                    });
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(() => {
                    if (this.reconnectAttempts < 10) {
                        this.reconnectAttempts++;
                        this.initWebSocket();
                    }
                }, 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        },

        sendMessage() {
            if (this.newMessage.trim() && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ message: this.newMessage.trim() }));
                this.newMessage = '';
            }
        }
    }
}
</script>
```

---

### `app/templates/partials/competition_items.html`

```html
{% for comp in competitions %}
<div class="card mb-3">
    <div class="card-body">
        <h5 class="card-title">{{ comp.name }}</h5>
        <p class="card-text">{{ comp.city }}, {{ comp.venue or 'Место не указано' }}</p>
        <p><strong>Дата:</strong> {{ comp.start_date.strftime('%d.%m.%Y') }} - {{ comp.end_date.strftime('%d.%m.%Y') }}</p>
        <span class="badge bg-secondary">{{ comp.status }}</span>
        <a href="/competitions/{{ comp.id }}/page" class="btn btn-sm btn-primary float-end ms-2">Подробнее</a>
        <button class="btn btn-sm btn-danger float-end" onclick="deleteCompetition({{ comp.id }})">Удалить</button>
    </div>
</div>
{% else %}
<div class="alert alert-info">Соревнований не найдено</div>
{% endfor %}

<script>
function deleteCompetition(compId) {
    if (confirm('Удалить соревнование?')) {
        fetch(`/competitions/${compId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        }).then(() => {
            location.reload();
        });
    }
}
</script>
```

---

### `app/templates/partials/confirm_modal.html`

```html
<!-- Модальное окно подтверждения -->
<div x-data="{ show: false, action: null, message: '' }"
     x-init="window.confirmModal = (msg, callback) => { message = msg; action = callback; show = true; }">
    <div x-show="show"
         class="modal fade show"
         style="display: block; background-color: rgba(0,0,0,0.5)"
         @click.away="show = false">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Подтверждение действия</h5>
                    <button type="button" class="btn-close" @click="show = false"></button>
                </div>
                <div class="modal-body">
                    <p x-text="message"></p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="show = false">Отмена</button>
                    <button type="button" class="btn btn-danger" @click="action(); show = false">Подтвердить</button>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

### `app/templates/partials/news_items.html`

```html
{% for news in news_list %}
<div class="card mb-3">
    <div class="card-body">
        <h5 class="card-title">{{ news.title }}</h5>
        <p class="card-text">{{ news.content[:200] }}...</p>
        <small class="text-muted">{{ news.published_at.strftime('%d.%m.%Y') if news.published_at else 'Черновик' }}</small>
        <a href="/news/{{ news.id }}" class="btn btn-sm btn-primary float-end ms-2">Читать</a>
        <button class="btn btn-sm btn-danger float-end" onclick="deleteNews({{ news.id }})">Удалить</button>
    </div>
</div>
{% else %}
<div class="alert alert-info">Новостей не найдено</div>
{% endfor %}

<script>
function deleteNews(newsId) {
    if (confirm('Удалить эту новость?')) {
        const token = document.cookie.match(/access_token=([^;]+)/)?.[1];
        fetch(`/news/${newsId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).then(() => {
            location.reload();
        });
    }
}
</script>
```

---

### `app/templates/partials/school_items.html`

```html
<div class="row">
    {% for school in schools %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm">
            {% if school.logo_url %}
            <img src="{{ school.logo_url }}" class="card-img-top" alt="{{ school.name }}" style="height: 150px; object-fit: cover;">
            {% else %}
            <div class="card-img-top bg-primary d-flex align-items-center justify-content-center" style="height: 150px;">
                <i class="fas fa-school fa-4x text-white"></i>
            </div>
            {% endif %}
            <div class="card-body">
                <h5 class="card-title">{{ school.name }}</h5>
                <p class="card-text text-muted">
                    <i class="fas fa-map-marker-alt"></i> {{ school.city }}
                </p>
                <p class="card-text">{{ school.description[:100] if school.description else 'Нет описания' }}...</p>
                {% if school.founded_year %}
                <p class="card-text"><small class="text-muted">Основана: {{ school.founded_year }}</small></p>
                {% endif %}
            </div>
            <div class="card-footer bg-transparent">
                <a href="/schools/{{ school.id }}/page" class="btn btn-primary w-100">Подробнее</a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <div class="alert alert-info">Школ не найдено</div>
    </div>
    {% endfor %}
</div>

{% if pages > 1 %}
<nav class="mt-4">
    <ul class="pagination justify-content-center">
        {% for p in range(1, pages + 1) %}
        <li class="page-item {% if p == page %}active{% endif %}">
            <a class="page-link" href="#" onclick="loadPage({{ p }}); return false;">{{ p }}</a>
        </li>
        {% endfor %}
    </ul>
</nav>

<script>
function loadPage(page) {
    const name = encodeURIComponent(document.getElementById('nameSearch').value);
    const city = encodeURIComponent(document.getElementById('citySearch').value);
    fetch(`/schools/search?name=${name}&city=${city}&page=${page}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('schoolsList').innerHTML = html;
        });
}
</script>
{% endif %}
```

---

### `app/templates/profile.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <!-- Информация о пользователе -->
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Личный кабинет</h3>

                <div x-data="profile()" x-init="loadProfile()">
                    <div x-show="loading" class="text-center">Загрузка...</div>
                    <div x-show="!loading && error" class="alert alert-danger" x-text="error"></div>

                    <div x-show="!loading && !error">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">ID</label>
                                    <p class="form-control-plaintext" x-text="user.id"></p>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Email</label>
                                    <p class="form-control-plaintext" x-text="user.email"></p>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Имя пользователя</label>
                                    <p class="form-control-plaintext" x-text="user.username"></p>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Полное имя</label>
                                    <p class="form-control-plaintext" x-text="user.full_name"></p>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Роль</label>
                                    <p class="form-control-plaintext" x-text="user.role"></p>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Дата регистрации</label>
                                    <p class="form-control-plaintext" x-text="new Date(user.created_at).toLocaleString()"></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Личные рекорды - проверяем role.name или role.value -->
        {% if current_user and (current_user.role.name == 'ATHLETE' or current_user.role.value == 'athlete') %}
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-medal"></i> Мои личные рекорды</h5>
            </div>
            <div class="card-body">
                <form id="addRecordForm" class="mb-4 p-3 bg-light rounded">
                    <div class="row g-2">
                        <div class="col-md-4">
                            <label class="form-label small">Дистанция</label>
                            <select class="form-select form-select-sm" id="distance" required>
                                <option value="">Выберите</option>
                                <option value="50">50 метров</option>
                                <option value="100">100 метров</option>
                                <option value="200">200 метров</option>
                                <option value="400">400 метров</option>
                                <option value="800">800 метров</option>
                                <option value="1500">1500 метров</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small">Стиль</label>
                            <select class="form-select form-select-sm" id="stroke" required>
                                <option value="">Выберите</option>
                                <option value="freestyle">Вольный стиль</option>
                                <option value="breaststroke">Брасс</option>
                                <option value="backstroke">На спине</option>
                                <option value="butterfly">Баттерфляй</option>
                                <option value="medley">Комплекс</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label small">Время (секунды)</label>
                            <input type="number" step="0.01" class="form-control form-control-sm" id="timeSeconds" placeholder="Например: 25.5" required>
                        </div>
                        <div class="col-md-1 d-flex align-items-end">
                            <button type="submit" class="btn btn-primary btn-sm w-100">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                </form>

                <div id="recordsList">
                    <div class="text-center py-3">
                        <div class="spinner-border text-primary spinner-border-sm" role="status"></div>
                        <span class="ms-2">Загрузка...</span>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="d-grid gap-2 mt-3">
            <a href="/" class="btn btn-secondary">На главную</a>
            <button onclick="logout()" class="btn btn-danger">Выйти</button>
        </div>
    </div>
</div>

<script>
function profile() {
    return {
        user: null,
        loading: true,
        error: '',

        async loadProfile() {
            this.loading = true;
            try {
                const response = await fetch('/auth/me', { credentials: 'include' });
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                if (response.ok) {
                    this.user = await response.json();
                    console.log('User loaded:', this.user);
                } else {
                    this.error = 'Не удалось загрузить профиль';
                }
            } catch (err) {
                this.error = 'Ошибка сети';
            } finally {
                this.loading = false;
            }
        }
    }
}

function logout() {
    fetch('/auth/logout', { method: 'POST', credentials: 'include' })
        .then(() => window.location.href = '/');
}

async function loadRecords() {
    try {
        const response = await fetch('/athletes/my/personal-bests', { credentials: 'include' });
        if (!response.ok) throw new Error('Ошибка загрузки');
        const records = await response.json();
        
        if (records.length === 0) {
            document.getElementById('recordsList').innerHTML = '<p class="text-muted text-center py-3 mb-0">Нет личных рекордов. Добавьте свой первый рекорд!</p>';
            return;
        }
        
        const grouped = {};
        records.forEach(record => {
            const key = `${record.distance}м`;
            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(record);
        });
        
        const strokeNames = {
            'freestyle': 'Вольный стиль', 'breaststroke': 'Брасс',
            'backstroke': 'На спине', 'butterfly': 'Баттерфляй', 'medley': 'Комплекс'
        };
        
        let html = '';
        for (const [distance, items] of Object.entries(grouped)) {
            html += `<h6 class="mt-3">${distance}</h6>`;
            html += `<div class="table-responsive"><table class="table table-sm table-striped">
                <thead><tr><th>Стиль</th><th>Время (сек)</th><th>Дата</th><th></th></tr></thead><tbody>`;
            items.forEach(record => {
                html += `
                    <tr>
                        <td>${strokeNames[record.stroke] || record.stroke}</td>
                        <td><strong>${record.time_seconds}</strong></td>
                        <td>${record.set_at ? new Date(record.set_at).toLocaleDateString() : '-'}</td>
                        <td><button class="btn btn-sm btn-danger" onclick="deleteRecord(${record.id})"><i class="fas fa-trash"></i></button></td>
                    </tr>
                `;
            });
            html += `</tbody></table></div>`;
        }
        document.getElementById('recordsList').innerHTML = html;
    } catch (error) {
        document.getElementById('recordsList').innerHTML = '<p class="text-danger text-center py-3 mb-0">Ошибка загрузки рекордов</p>';
    }
}

const form = document.getElementById('addRecordForm');
if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const distance = document.getElementById('distance').value;
        const stroke = document.getElementById('stroke').value;
        const timeSeconds = document.getElementById('timeSeconds').value;
        
        if (!distance || !stroke || !timeSeconds) {
            alert('Заполните все поля');
            return;
        }
        
        try {
            const response = await fetch('/athletes/my/personal-bests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    distance: parseInt(distance),
                    stroke: stroke,
                    time_seconds: parseFloat(timeSeconds)
                }),
                credentials: 'include'
            });
            
            if (response.ok) {
                document.getElementById('timeSeconds').value = '';
                document.getElementById('distance').value = '';
                document.getElementById('stroke').value = '';
                alert('Рекорд добавлен!');
                loadRecords();
            } else {
                const error = await response.json();
                alert(error.detail || 'Ошибка добавления');
            }
        } catch (error) {
            alert('Ошибка сети');
        }
    });
}

window.deleteRecord = async function(recordId) {
    if (confirm('Удалить этот рекорд?')) {
        try {
            const response = await fetch(`/athletes/personal-bests/${recordId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            if (response.ok) {
                alert('Рекорд удален');
                loadRecords();
            } else {
                alert('Ошибка удаления');
            }
        } catch (error) {
            alert('Ошибка сети');
        }
    }
};

{% if current_user and (current_user.role.name == 'ATHLETE' or current_user.role.value == 'athlete') %}
document.addEventListener('DOMContentLoaded', loadRecords);
{% endif %}
</script>
{% endblock %}
<script>
// ... существующий код ...

// Функция удаления рекорда с CSRF токеном
window.deleteRecord = async function(recordId) {
    if (confirm('Удалить этот рекорд?')) {
        // Получаем CSRF токен из cookie
        const csrfMatch = document.cookie.match(/csrf_token=([^;]+)/);
        const csrfToken = csrfMatch ? csrfMatch[1] : '';
        
        try {
            const response = await fetch(`/athletes/personal-bests/${recordId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'X-CSRF-Token': csrfToken
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                alert('Рекорд удален');
                loadRecords(); // Перезагружаем список
            } else {
                const error = await response.json();
                alert(error.detail || 'Ошибка удаления');
            }
        } catch (error) {
            alert('Ошибка сети');
        }
    }
};
</script>
```

---

### `app/templates/register.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Регистрация</h3>

                <form x-data="registerForm()" @submit.prevent="register">
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" x-model="email" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Имя пользователя</label>
                        <input type="text" class="form-control" x-model="username" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Полное имя</label>
                        <input type="text" class="form-control" x-model="full_name" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Пароль</label>
                        <div class="input-group">
                            <input :type="showPassword ? 'text' : 'password'" class="form-control" x-model="password" required>
                            <button class="btn btn-outline-secondary" type="button" @click="showPassword = !showPassword">
                                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                            </button>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Роль</label>
                        <select class="form-select" x-model="role">
                            <option value="athlete">Спортсмен</option>
                            <option value="coach">Тренер</option>
                            <option value="school_rep">Представитель школы</option>
                        </select>
                    </div>

                    <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                        <span x-show="!loading">Зарегистрироваться</span>
                        <span x-show="loading">Загрузка...</span>
                    </button>

                    <div x-show="errorMessage" class="alert alert-danger mt-3" x-text="errorMessage"></div>
                    <div x-show="successMessage" class="alert alert-success mt-3" x-text="successMessage"></div>
                </form>

                <div class="text-center mt-3">
                    <a href="/login">Уже есть аккаунт? Войти</a>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function registerForm() {
    return {
        email: '',
        username: '',
        full_name: '',
        password: '',
        role: 'athlete',
        showPassword: false,
        loading: false,
        errorMessage: '',
        successMessage: '',

        async register() {
            this.loading = true;
            this.errorMessage = '';
            this.successMessage = '';

            try {
                const response = await fetch('/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: this.email,
                        username: this.username,
                        full_name: this.full_name,
                        password: this.password,
                        role: this.role
                    }),
                    credentials: 'include'
                });

                const data = await response.json();

                if (response.ok) {
                    this.successMessage = 'Регистрация успешна! Перенаправление на вход...';
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                } else {
                    this.errorMessage = data.detail || 'Ошибка регистрации';
                }
            } catch (error) {
                this.errorMessage = 'Ошибка сети';
            } finally {
                this.loading = false;
            }
        }
    }
}
</script>
{% endblock %}
```

---

### `app/templates/school_detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <!-- Обложка -->
        <div class="position-relative mb-4">
            {% if school.cover_url %}
            <img src="{{ school.cover_url }}" class="w-100" style="height: 300px; object-fit: cover; border-radius: 10px;">
            {% else %}
            <div class="bg-primary d-flex align-items-center justify-content-center" style="height: 300px; border-radius: 10px;">
                <i class="fas fa-school fa-5x text-white"></i>
            </div>
            {% endif %}
        </div>
        
        <!-- Информация о школе -->
        <div class="card mb-4">
            <div class="card-body">
                <h1>{{ school.name }}</h1>
                {% if school.founder %}
                <p><strong>Основатель:</strong> {{ school.founder }}</p>
                {% endif %}
                {% if school.founded_year %}
                <p><strong>Год основания:</strong> {{ school.founded_year }}</p>
                {% endif %}
                <p><strong>Город:</strong> {{ school.city }}</p>
                <p><strong>Адрес:</strong> {{ school.address }}</p>
                {% if school.phone %}
                <p><strong>Телефон:</strong> {{ school.phone }}</p>
                {% endif %}
                {% if school.email %}
                <p><strong>Email:</strong> {{ school.email }}</p>
                {% endif %}
                <p>{{ school.description }}</p>
            </div>
        </div>
        
        <!-- Главный тренер школы -->
        {% if head_coach %}
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Главный тренер школы</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3 text-center">
                        {% if head_coach.photo_url %}
                        <img src="{{ head_coach.photo_url }}" class="rounded-circle" style="width: 150px; height: 150px; object-fit: cover;">
                        {% else %}
                        <i class="fas fa-user-circle fa-5x text-secondary"></i>
                        {% endif %}
                    </div>
                    <div class="col-md-9">
                        <h4>{{ head_coach.user.full_name }}</h4>
                        <p><strong>Квалификация:</strong> {{ head_coach.qualification or 'Не указана' }}</p>
                        <p><strong>Стаж:</strong> {{ head_coach.experience_years or 0 }} лет</p>
                        <p><strong>Специализация:</strong> {{ head_coach.specialization or 'Не указана' }}</p>
                        <a href="/coaches/{{ head_coach.id }}/page" class="btn btn-outline-primary">Подробнее</a>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Филиалы -->
        <div class="card mb-4">
            <div class="card-header">
                <h5>Филиалы</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for branch in branches %}
                    <div class="col-md-6 mb-3">
                        <div class="card h-100">
                            <div class="card-body">
                                <h5 class="card-title">{{ branch.name }}</h5>
                                <p class="card-text">
                                    <strong>Адрес:</strong> {{ branch.address }}<br>
                                    {% if branch.phone %}<strong>Телефон:</strong> {{ branch.phone }}{% endif %}
                                </p>
                                <a href="/branches/{{ branch.id }}/page" class="btn btn-sm btn-outline-primary">Подробнее о филиале</a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### `app/templates/schools_list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="text-center mb-4">Школы плавания</h1>
        
        <div class="card mb-4">
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-md-5">
                        <input type="text" class="form-control" id="nameSearch" placeholder="Название школы" oninput="searchSchools()">
                    </div>
                    <div class="col-md-5">
                        <input type="text" class="form-control" id="citySearch" placeholder="Город" oninput="searchSchools()">
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-secondary w-100" onclick="resetFilters()">Сбросить</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="schoolsList">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function searchSchools() {
    const name = encodeURIComponent(document.getElementById('nameSearch').value);
    const city = encodeURIComponent(document.getElementById('citySearch').value);
    
    fetch(`/schools/search?name=${name}&city=${city}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('schoolsList').innerHTML = html;
        });
}

function resetFilters() {
    document.getElementById('nameSearch').value = '';
    document.getElementById('citySearch').value = '';
    searchSchools();
}

document.addEventListener('DOMContentLoaded', searchSchools);
</script>
{% endblock %}
```

---

### `app/templates/test.html`

```html
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<h1>Jinja2 работает!</h1>
</body>
</html>
```

---

### `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: swimming-postgres
    environment:
      POSTGRES_USER: swimming_user
      POSTGRES_PASSWORD: swimming_pass
      POSTGRES_DB: swimming_portal
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

---

### `docs/pages/athlete-detail.md`

```markdown
# Профиль спортсмена

## 1. Маршрут
`GET /athletes/{athlete_id}`
Шаблон: `app/templates/athlete_detail.html`

## 2. Назначение
Публичный профиль спортсмена:
личные данные, школа, тренер, личные рекорды,
история участия в соревнованиях.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Обложка (cover_url или от школы)
- Фото спортсмена (photo_url)
- Имя, дата рождения, пол, разряд
- Школа и тренер (со ссылками)
- Личные рекорды (PersonalBest)
  - по дисциплинам (дистанция + стиль + время)
- История заявок и результатов (Entry + HeatEntry)

## 5. Данные
- AthleteProfile (все поля)
- User (full_name)
- School (name)
- CoachProfile (имя тренера)
- PersonalBest[] (личные рекорды)
- Entry[] с результатами

## 6. Личные рекорды
Дисциплины:
- Дистанции: 50, 100, 200, 400, 800, 1500 м
- Стили: freestyle, breaststroke, backstroke,
  butterfly, medley
- Время в формате MM:SS.ms

## 7. Логика и поведение
- Если спортсмен не найден — 404
- Обложка: своя → школьная → заглушка
- Кнопка редактирования видна только самому
  спортсмену (current_user.id == athlete.user_id)
  или admin/coach

## 8. Связанные файлы
- `app/templates/athlete_detail.html`
- `app/routers/athletes.py`
- `app/services/athlete_service.py`
- `app/repositories/athlete_profile_repository.py`
- `app/repositories/personal_best_repository.py`

## 9. Критерии готовности
- [ ] Данные спортсмена отображаются
- [ ] Личные рекорды видны в удобном формате
- [ ] Ссылки на школу и тренера работают
- [ ] 404 при отсутствии
- [ ] Редактирование только для своих
```

---

### `docs/pages/coach-detail.md`

```markdown
# Профиль тренера

## 1. Маршрут
`GET /coaches/{coach_id}`
Шаблон: `app/templates/coach_detail.html`

## 2. Назначение
Публичный профиль тренера:
квалификация, специализация, список учеников.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Обложка (cover_url или от школы)
- Фото тренера (photo_url)
- Имя, квалификация, специализация
- Опыт (experience_years)
- Достижения (achievements)
- Биография (bio)
- Школа и филиал (со ссылками)
- Список учеников (AthleteProfile)

## 5. Данные
- CoachProfile (все поля)
- User (full_name)
- School (name)
- Branch (name)
- AthleteProfile[] (ученики)

## 6. Логика и поведение
- Если тренер не найден — 404
- Обложка: своя → школьная → заглушка
- Кнопка редактирования только для самого тренера
  или admin

## 7. Связанные файлы
- `app/templates/coach_detail.html`
- `app/routers/coaches.py`
- `app/routers/coach_profiles.py`
- `app/services/coach_service.py`

## 8. Критерии готовности
- [ ] Все данные тренера отображаются
- [ ] Список учеников виден
- [ ] Ссылка на школу работает
- [ ] 404 при отсутствии
```

---

### `docs/pages/competition-detail.md`

```markdown
# Детальная страница соревнования

## 1. Маршрут
`GET /competitions/{competition_id}/page`
Шаблон: `app/templates/competition_detail.html`

## 2. Назначение
Полная информация о соревновании:
дисциплины, участники, результаты, возрастные категории.
Скачивание стартового листа и результатов.

## 3. Доступ
Публичная. Некоторые действия только для авторизованных.

## 4. Основные блоки
- Заголовок (название, статус, даты, место)
- Описание соревнования
- Возрастные категории
- Список дисциплин (SwimEvent)
- Участники по дисциплинам (Entry)
- Заплывы и результаты (Heat/HeatEntry)
- Кнопки скачивания PDF и CSV
- Кнопка "Подать заявку" (для athlete)
- Чат соревнования

## 5. Данные
- Competition (id, name, description, dates, venue, city, status)
- AgeCategory[] (возрастные категории)
- SwimEvent[] (дисциплины)
- Entry[] (заявки)
- Heat[] с HeatEntry[] (заплывы и результаты)

## 6. Логика и поведение
- Если competition не найдено — 404
- Кнопка "Подать заявку" видна только role=athlete
  и только если status=active
- Кнопки редактирования видны только admin/secretary
- PDF: GET /competitions/{id}/start-list.pdf
- PDF результаты: GET /competitions/{id}/results.pdf
- CSV результаты: GET /competitions/{id}/results.csv

## 7. Состояния
- Loading
- Not found: 404
- Нет дисциплин: "Дисциплины ещё не добавлены"
- Нет участников: "Заявок ещё нет"

## 8. Связанные файлы
- `app/templates/competition_detail.html`
- `app/routers/competitions.py`
- `app/routers/entries.py`
- `app/routers/heats.py`
- `app/services/competition_service.py`
- `app/services/pdf_service.py`
- `app/services/csv_service.py`

## 9. Критерии готовности
- [ ] Все данные соревнования отображаются
- [ ] Дисциплины и участники видны
- [ ] PDF и CSV скачиваются
- [ ] Кнопка заявки видна только athlete при active статусе
- [ ] Чат работает
- [ ] 404 при отсутствии соревнования
```

---

### `docs/pages/competitions-list.md`

```markdown
# Список соревнований

## 1. Маршрут
`GET /competitions/page`
Шаблон: `app/templates/competitions_list.html`

## 2. Назначение
Отображает все соревнования портала.
Позволяет искать и фильтровать по названию, городу, статусу.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Заголовок страницы
- Панель поиска и фильтров (название, город, статус)
- Список карточек соревнований
- Пагинация

## 5. Данные
- Список Competition из БД
- Поля: id, name, description, start_date, end_date,
  venue, city, status, max_participants

## 6. Статусы соревнований
- draft — черновик
- active — идёт регистрация
- completed — завершено

## 7. Логика и поведение
- При загрузке показываются все соревнования
- Поиск через GET /competitions/search (HTMX partial)
- Частичное обновление через partials/competition_items.html
- Фильтры: name (строка), city (строка), status (выбор)
- Пагинация: page параметр

## 8. Состояния
- Loading: skeleton карточек
- Empty: "Соревнований не найдено"
- Error: сообщение об ошибке

## 9. Карточка соревнования
- Название
- Город и место проведения
- Даты (start_date — end_date)
- Статус (бейдж)
- Кнопка "Подробнее" → /competitions/{id}/page

## 10. Связанные файлы
- `app/templates/competitions_list.html`
- `app/templates/partials/competition_items.html`
- `app/routers/competitions.py`
- `app/services/competition_service.py`

## 11. Критерии готовности
- [ ] Список соревнований отображается
- [ ] Поиск и фильтры работают
- [ ] Пагинация работает
- [ ] Empty state есть
- [ ] Карточки ведут на детальную страницу
```

---

### `docs/pages/live.md`

```markdown
# Live результаты

## 1. Маршрут
`GET /live`
Шаблон: `app/templates/live.html`

## 2. Назначение
Отображение результатов соревнований в реальном времени.
Обновление без перезагрузки страницы.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Выбор активного соревнования
- Текущий заплыв (Heat)
- Таблица участников заплыва с результатами
- Чат соревнования

## 5. Данные
- Активные соревнования (status=active)
- Текущий Heat (status=scheduled или started)
- HeatEntry[] с результатами
- ChatMessage[] для комнаты competition_{id}

## 6. Логика и поведение
- Автообновление таблицы результатов
  (polling или WebSocket через /chat)
- Чат работает через WebSocket
- Результаты обновляются в реальном времени

## 7. Связанные файлы
- `app/templates/live.html`
- `app/templates/partials/chat.html`
- `app/routers/chat.py`
- `app/routers/heats.py`
- `app/services/chat_service.py`
- `app/services/heat_service.py`
- `app/main.py` → GET /live

## 8. Критерии готовности
- [ ] Активные соревнования загружаются
- [ ] Результаты обновляются в реальном времени
- [ ] Чат работает
- [ ] Страница работает без авторизации
```

---

### `docs/pages/news-list.md`

```markdown
# Список новостей

## 1. Маршрут
`GET /news/`
Шаблон: `app/templates/news_list.html`

## 2. Назначение
Лента новостей портала.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Заголовок
- Список карточек новостей
- Пагинация

## 5. Данные
Поля News:
- id, title, content (краткое), author, published_at

## 6. Карточка новости
- Заголовок
- Дата публикации
- Автор
- Краткое превью текста
- Кнопка "Читать" → /news/{id}

## 7. Логика и поведение
- Показывать только is_published=True
- Сортировка по published_at DESC
- Частичное обновление через partials/news_items.html

## 8. Состояния
- Empty: "Новостей пока нет"
- Error: сообщение

## 9. Связанные файлы
- `app/templates/news_list.html`
- `app/templates/partials/news_items.html`
- `app/routers/news.py`
- `app/services/news_service.py`

## 10. Критерии готовности
- [ ] Список новостей отображается
- [ ] Только опубликованные новости
- [ ] Карточки ведут на детальную страницу
```

---

### `docs/pages/profile.md`

```markdown
# Личный кабинет

## 1. Маршрут
`GET /profile`
Шаблон: `app/templates/profile.html`

## 2. Назначение
Персональная страница пользователя.
Показывает данные профиля, ссылки на профиль
спортсмена или тренера в зависимости от роли.

## 3. Доступ
Только авторизованные пользователи.
Неавторизованных — редирект на /login.

## 4. Основные блоки
- Аватар и основные данные (имя, email, роль)
- Кнопка редактирования профиля
- Блок для роли athlete: ссылка на AthleteProfile
- Блок для роли coach: ссылка на CoachProfile + дашборд
- Список заявок на соревнования (для athlete)
- Последние действия

## 5. Данные
- current_user (из cookie JWT)
- athlete_profile (если роль athlete)
- coach_profile (если роль coach)

## 6. Логика и поведение
- Определить роль пользователя и показать соответствующие блоки
- Ссылка на /athletes/{id} для спортсмена
- Ссылка на /coaches/{id} и /coach-dashboard для тренера

## 7. Связанные файлы
- `app/templates/profile.html`
- `app/main.py` → GET /profile
- `app/auth.py` → get_current_user_optional_cookie

## 8. Критерии готовности
- [ ] Неавторизованные редиректируются
- [ ] Данные пользователя отображаются
- [ ] Блоки по ролям работают корректно
- [ ] Ссылки на профили работают
```

---

### `docs/pages/register.md`

```markdown
# Страница регистрации

## 1. Маршрут
`GET /register`
Шаблон: `app/templates/register.html`
API: `POST /auth/register`

## 2. Назначение
Регистрация нового пользователя на портале.
По умолчанию роль — guest.

## 3. Доступ
Публичная. Авторизованных редиректить на /profile.

## 4. Поля формы
- Имя (full_name)
- Username
- Email
- Пароль
- Подтверждение пароля
- Кнопка "Зарегистрироваться"
- Ссылка "Уже есть аккаунт? Войти"

## 5. Логика и поведение
- Валидация на фронте: совпадение паролей, минимальная длина
- POST /auth/register
- При успехе: редирект на /login с сообщением "Вы успешно зарегистрированы"
- При ошибке (email занят, username занят): понятное сообщение
- После регистрации отправляется welcome email

## 6. Состояния
- Idle
- Loading
- Error (с текстом ошибки)
- Success (редирект)

## 7. Связанные файлы
- `app/templates/register.html`
- `app/routers/auth.py` → POST /auth/register
- `app/services/auth_service.py`
- `app/core/email.py`
- `app/templates/emails/welcome.html`

## 8. Критерии готовности
- [ ] Все поля валидируются
- [ ] Ошибки отображаются понятно
- [ ] После регистрации редирект работает
- [ ] Welcome email отправляется
```

---

### `docs/pages/school-detail.md`

```markdown
# Детальная страница школы

## 1. Маршрут
`GET /schools/{school_id}`
Шаблон: `app/templates/school_detail.html`

## 2. Назначение
Полная информация о школе плавания:
история, тренеры, спортсмены, филиалы.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Обложка школы (cover_url)
- Логотип + название + город
- Контакты (телефон, email, сайт, адрес)
- Описание школы
- Год основания и основатель
- Список филиалов (Branch)
- Список тренеров (CoachProfile)
- Список спортсменов (AthleteProfile)

## 5. Данные
- School (все поля)
- Branch[] (филиалы)
- CoachProfile[] (тренеры школы)
- AthleteProfile[] (спортсмены школы)

## 6. Логика и поведение
- Если школа не найдена — 404
- Если нет логотипа — показать заглушку
- Кнопки редактирования видны только admin/school_rep

## 7. Связанные файлы
- `app/templates/school_detail.html`
- `app/routers/schools.py`
- `app/services/school_service.py`
- `app/repositories/school_repository.py`

## 8. Критерии готовности
- [ ] Все данные школы отображаются
- [ ] Тренеры и спортсмены видны
- [ ] Филиалы видны и кликабельны
- [ ] 404 при отсутствии школы
```

---

### `docs/pages/schools-list.md`

```markdown
# Список школ плавания

## 1. Маршрут
`GET /schools/`
Шаблон: `app/templates/schools_list.html`

## 2. Назначение
Каталог всех школ плавания на портале.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Заголовок
- Поиск по школам
- Список карточек школ
- Пагинация

## 5. Данные
Поля School:
- id, name, city, description
- logo_url, cover_url
- phone, email, website
- branches (количество филиалов)

## 6. Карточка школы
- Логотип
- Название
- Город
- Краткое описание
- Количество тренеров и спортсменов
- Кнопка "Подробнее" → /schools/{id}

## 7. Логика и поведение
- Показывать только is_active=True школы
- Поиск по названию и городу
- Частичное обновление через partials/school_items.html

## 8. Состояния
- Loading: skeleton
- Empty: "Школы не найдены"
- Error: сообщение

## 9. Связанные файлы
- `app/templates/schools_list.html`
- `app/templates/partials/school_items.html`
- `app/routers/schools.py`
- `app/services/school_service.py`

## 10. Критерии готовности
- [ ] Список школ отображается
- [ ] Поиск работает
- [ ] Карточки ведут на детальную страницу
- [ ] Empty state есть
```

---

### `init_production_db.py`

```python
import asyncio
from sqlalchemy import text
from app.database import engine, Base
from app.models import *
from app.core.logging_config import logger

async def init_production_db():
    """Инициализация production базы данных"""
    try:
        async with engine.begin() as conn:
            # Создаем все таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Все таблицы успешно созданы")
            
            # Проверяем созданные таблицы
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            logger.info(f"📊 Создано таблиц: {len(tables)}")
            for table in tables:
                logger.info(f"   - {table[0]}")
            
            # Создаем индексы по одному (asyncpg не поддерживает несколько команд)
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_room_created ON chat_messages(room, created_at DESC);",
                "CREATE INDEX IF NOT EXISTS idx_entries_competition_status ON entries(competition_id, status);",
                "CREATE INDEX IF NOT EXISTS idx_heat_entries_heat_lane ON heat_entries(heat_id, lane);",
                "CREATE INDEX IF NOT EXISTS idx_swim_events_competition ON swim_events(competition_id);",
                "CREATE INDEX IF NOT EXISTS idx_age_categories_competition ON age_categories(competition_id);",
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(text(index_sql))
                    logger.info(f"   ✅ Индекс создан")
                except Exception as e:
                    logger.warning(f"   ⚠️ Индекс уже существует или ошибка: {e}")
            
            await conn.commit()
            logger.info("✅ Все индексы созданы")
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_production_db())
```

---

### `requirements.txt`

```text
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.10
alembic==1.13.0
python-dotenv==1.0.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.12
jinja2==3.1.4
aiofiles==24.1.0
openpyxl==3.1.5
slowapi==0.1.9
sentry-sdk==2.19.0
structlog==25.2.0
email-validator==2.2.0
pydantic-settings==2.6.0
reportlab==4.2.5
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
factory-boy==3.3.1
faker==30.0.0
slowapi==0.1.9redis==5.0.8
aiosmtplib==3.0.2
```

---

---

## 🎯 ЗАДАЧА

> Впиши сюда задачу перед отправкой ИИ

```
[ОПИСАНИЕ ЗАДАЧИ]
```

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.config import settings

# Тестовая БД (используем отдельную)
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"


@pytest.fixture(scope="function")
async def db_engine():
    """Создаёт тестовый engine и очищает БД"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Очищаем после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Создаёт тестовую сессию БД"""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session):
    """Создаёт тестовый HTTP клиент"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def auth_headers(client):
    """Возвращает заголовки авторизации"""
    await client.post("/auth/register", json={
        "email": "admin@test.com",
        "username": "admin_test",
        "password": "admin123",
        "full_name": "Admin Test",
        "role": "admin"
    })
    
    response = await client.post("/auth/token", data={
        "username": "admin_test",
        "password": "admin123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import User, UserRole, School, Competition
from app.auth import get_password_hash
from datetime import datetime, timedelta, timezone

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Создаём админа
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        
        # Создаём школу
        school = School(
            name="Спортивная школа №1",
            city="Москва",
            address="ул. Спортивная, 1",
            description="Лучшая школа плавания",
            is_active=True
        )
        session.add(school)
        
        # Создаём соревнование
        competition = Competition(
            name="Чемпионат Москвы по плаванию",
            description="Ежегодные соревнования",
            start_date=datetime.now(timezone.utc) + timedelta(days=7),
            end_date=datetime.now(timezone.utc) + timedelta(days=9),
            venue="Дворец спорта",
            city="Москва",
            status="registration_open",
            max_participants=100
        )
        session.add(competition)
        
        await session.commit()
        print("✅ Тестовые данные добавлены")
        print(f"   - Админ: admin@example.com / admin123")
        print(f"   - Школа: {school.name}")
        print(f"   - Соревнование: {competition.name}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())

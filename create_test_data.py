import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.auth import get_password_hash

async def create_test_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Очищаем существующие данные (опционально)
        await session.execute(text("TRUNCATE TABLE \"user\", schools, coach_profiles, athlete_profiles, branches CASCADE;"))
        await session.commit()
        
        # 2. Создаём пользователей
        users_data = [
            {"email": "admin@swim.ru", "username": "admin", "password": "admin123", "full_name": "Администратор", "role": "admin"},
            {"email": "coach@swim.ru", "username": "coach", "password": "coach123", "full_name": "Иван Петров", "role": "coach"},
            {"email": "athlete@swim.ru", "username": "athlete", "password": "athlete123", "full_name": "Анна Сидорова", "role": "athlete"},
            {"email": "school@swim.ru", "username": "schoolrep", "password": "school123", "full_name": "Мария Иванова", "role": "school_rep"},
        ]
        
        users = {}
        for u in users_data:
            result = await session.execute(
                text("""
                    INSERT INTO \"user\" (email, username, hashed_password, full_name, role, is_active, created_at)
                    VALUES (:email, :username, :hashed_password, :full_name, :role, true, :created_at)
                    RETURNING id
                """),
                {
                    "email": u["email"],
                    "username": u["username"],
                    "hashed_password": get_password_hash(u["password"]),
                    "full_name": u["full_name"],
                    "role": u["role"],
                    "created_at": datetime.now(timezone.utc)
                }
            )
            user_id = result.scalar()
            users[u["username"]] = {"id": user_id, **u}
            print(f"✅ Создан пользователь: {u['username']} / {u['password']}")
        
        # 3. Создаём школу
        school_result = await session.execute(
            text("""
                INSERT INTO schools (name, full_name, city, address, description, founded_year, phone, email, website, is_active, created_at)
                VALUES (:name, :full_name, :city, :address, :description, :founded_year, :phone, :email, :website, true, :created_at)
                RETURNING id
            """),
            {
                "name": "СШОР по плаванию",
                "full_name": "Специализированная школа олимпийского резерва по плаванию",
                "city": "Москва",
                "address": "ул. Спортивная, д. 10",
                "description": "Лучшая школа плавания в Москве, подготовка чемпионов",
                "founded_year": 1995,
                "phone": "+7 (495) 123-45-67",
                "email": "info@swimschool.ru",
                "website": "https://swimschool.ru",
                "created_at": datetime.now(timezone.utc)
            }
        )
        school_id = school_result.scalar()
        print(f"✅ Создана школа: СШОР по плаванию (ID: {school_id})")
        
        # 4. Создаём филиал
        branch_result = await session.execute(
            text("""
                INSERT INTO branches (school_id, name, address, phone, email, is_active, created_at)
                VALUES (:school_id, :name, :address, :phone, :email, true, :created_at)
                RETURNING id
            """),
            {
                "school_id": school_id,
                "name": "Филиал на Юго-Западе",
                "address": "пр-т Вернадского, д. 25",
                "phone": "+7 (495) 987-65-43",
                "email": "southwest@swimschool.ru",
                "created_at": datetime.now(timezone.utc)
            }
        )
        branch_id = branch_result.scalar()
        print(f"✅ Создан филиал: Филиал на Юго-Западе (ID: {branch_id})")
        
        # 5. Создаём профиль тренера
        coach_result = await session.execute(
            text("""
                INSERT INTO coach_profiles (user_id, school_id, branch_id, qualification, experience_years, specialization, is_head_coach, bio, created_at, updated_at)
                VALUES (:user_id, :school_id, :branch_id, :qualification, :experience_years, :specialization, :is_head_coach, :bio, :created_at, :updated_at)
                RETURNING id
            """),
            {
                "user_id": users["coach"]["id"],
                "school_id": school_id,
                "branch_id": branch_id,
                "qualification": "Тренер высшей категории",
                "experience_years": 15,
                "specialization": "Кроль, баттерфляй",
                "is_head_coach": True,
                "bio": "Заслуженный тренер России, подготовил 5 мастеров спорта",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        )
        coach_id = coach_result.scalar()
        print(f"✅ Создан профиль тренера (ID: {coach_id})")
        
        # 6. Создаём профиль спортсмена
        athlete_result = await session.execute(
            text("""
                INSERT INTO athlete_profiles (user_id, school_id, branch_id, coach_id, birth_date, gender, rank, created_at, updated_at)
                VALUES (:user_id, :school_id, :branch_id, :coach_id, :birth_date, :gender, :rank, :created_at, :updated_at)
                RETURNING id
            """),
            {
                "user_id": users["athlete"]["id"],
                "school_id": school_id,
                "branch_id": branch_id,
                "coach_id": coach_id,
                "birth_date": datetime(2005, 6, 15, tzinfo=timezone.utc),
                "gender": "female",
                "rank": "КМС",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        )
        athlete_id = athlete_result.scalar()
        print(f"✅ Создан профиль спортсмена (ID: {athlete_id})")
        
        # 7. Добавляем личные рекорды спортсмена
        pbs = [
            {"distance": 50, "stroke": "freestyle", "time_seconds": 26.5},
            {"distance": 100, "stroke": "freestyle", "time_seconds": 58.2},
            {"distance": 200, "stroke": "freestyle", "time_seconds": 128.5},
            {"distance": 100, "stroke": "breaststroke", "time_seconds": 75.3},
        ]
        
        for pb in pbs:
            await session.execute(
                text("""
                    INSERT INTO personal_bests (athlete_id, distance, stroke, time_seconds, set_at)
                    VALUES (:athlete_id, :distance, :stroke, :time_seconds, :set_at)
                """),
                {
                    "athlete_id": athlete_id,
                    "distance": pb["distance"],
                    "stroke": pb["stroke"],
                    "time_seconds": pb["time_seconds"],
                    "set_at": datetime.now(timezone.utc)
                }
            )
        print(f"✅ Добавлено {len(pbs)} личных рекордов")
        
        # 8. Создаём соревнование
        competition_result = await session.execute(
            text("""
                INSERT INTO competitions (name, description, start_date, end_date, venue, city, status, max_participants, created_at, updated_at)
                VALUES (:name, :description, :start_date, :end_date, :venue, :city, :status, :max_participants, :created_at, :updated_at)
                RETURNING id
            """),
            {
                "name": "Чемпионат Москвы 2026",
                "description": "Открытый чемпионат города Москвы по плаванию",
                "start_date": datetime.now(timezone.utc) + timedelta(days=14),
                "end_date": datetime.now(timezone.utc) + timedelta(days=16),
                "venue": "Дворец водного спорта",
                "city": "Москва",
                "status": "registration_open",
                "max_participants": 200,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        )
        competition_id = competition_result.scalar()
        print(f"✅ Создано соревнование: Чемпионат Москвы 2026 (ID: {competition_id})")
        
        # 9. Создаём новость
        news_result = await session.execute(
            text("""
                INSERT INTO news (title, content, author_id, is_published, published_at, created_at, updated_at)
                VALUES (:title, :content, :author_id, true, :published_at, :created_at, :updated_at)
                RETURNING id
            """),
            {
                "title": "Открыта регистрация на Чемпионат Москвы",
                "content": "Уважаемые спортсмены и тренеры! Открыта регистрация на Чемпионат Москвы по плаванию. Регистрация продлится до 1 мая.",
                "author_id": users["admin"]["id"],
                "published_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        )
        print(f"✅ Создана новость")
        
        await session.commit()
        
        print("\n" + "="*50)
        print("✅ ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО ДОБАВЛЕНЫ")
        print("="*50)
        print("\n👤 Пользователи для входа:")
        print("   Администратор: admin@swim.ru / admin123")
        print("   Тренер: coach@swim.ru / coach123")
        print("   Спортсмен: athlete@swim.ru / athlete123")
        print("   Представитель школы: schoolrep@swim.ru / school123")
        print("\n🏊 Ссылки:")
        print("   Главная: http://localhost:8000")
        print("   Школы: http://localhost:8000/schools/page")
        print("   Соревнования: http://localhost:8000/competitions/page")
        print("   Новости: http://localhost:8000/news/page")
        print("   Профиль тренера: http://localhost:8000/coaches/1/page")
        print("   Профиль спортсмена: http://localhost:8000/athletes/1/page")
        print("   Live: http://localhost:8000/live")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_data())

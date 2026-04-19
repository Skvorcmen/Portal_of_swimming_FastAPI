import asyncio
from sqlalchemy import select, text
from app.database import engine, async_session_maker
from app.models import Base, User, UserRole


async def test_connection():
    try:
        print("1. Создаём таблицы...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы!")

        print("2. Добавляем тестового пользователя...")
        async with async_session_maker() as session:
            # Проверяем, есть ли уже такой пользователь
            stmt = select(User).where(User.username == "admin")
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                test_user = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password="fake_hash_for_now",
                    full_name="Admin User",
                    role=UserRole.ADMIN,
                )
                session.add(test_user)
                await session.commit()
                print("✅ Пользователь создан!")
            else:
                print("✅ Пользователь уже существует!")

            # Читаем пользователя из БД (правильный способ)
            stmt = select(User).where(User.username == "admin")
            result = await session.execute(stmt)
            user = result.scalar_one()
            print(
                f"✅ Найден пользователь: {user.full_name} (id={user.id}, роль={user.role.value})"
            )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await engine.dispose()
        print("3. Соединение с БД закрыто")


if __name__ == "__main__":
    asyncio.run(test_connection())

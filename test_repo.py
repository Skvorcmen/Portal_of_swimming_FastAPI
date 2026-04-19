import asyncio
from app.database import async_session_maker
from app.repositories.user_repository import UserRepository


async def test_repo():
    async with async_session_maker() as session:
        repo = UserRepository(session)

        # Найти пользователя по username
        user = await repo.get_by_username("step1")
        if user:
            print(f"✅ Найден пользователь: {user.username} (id={user.id})")
        else:
            print("❌ Пользователь не найден")

        # Получить всех пользователей
        all_users = await repo.get_all()
        print(f"✅ Всего пользователей: {len(all_users)}")


if __name__ == "__main__":
    asyncio.run(test_repo())

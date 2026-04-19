import asyncio

from app.database import async_session_maker
from app.models import UserRole
from app.services.auth_service import AuthService


async def test_service():
    async with async_session_maker() as session:
        service = AuthService(session)

        # Тест: регистрация нового пользователя
        print("1. Регистрация нового пользователя...")
        success, user, error = await service.register_user(
            email="service@test.com",
            username="serviceuser",
            password="123",
            full_name="Service User",
            role=UserRole.ATHLETE,
        )

        if success and user:
            print(
                f"   ✅ Зарегистрирован: {user.username} (id={user.id})"
            )
        else:
            print(f"   ❌ Ошибка: {error}")

        # Тест: логин
        print("\n2. Логин...")
        success, token, error = await service.login_user("serviceuser", "123")

        if success:
            print(f"   ✅ Токен получен: {token[:50]}...")
        else:
            print(f"   ❌ Ошибка: {error}")

        # Тест: неверный пароль
        print("\n3. Логин с неверным паролем...")
        success, token, error = await service.login_user("serviceuser", "wrongpassword")

        if not success:
            print(f"   ✅ Ожидаемая ошибка: {error}")


if __name__ == "__main__":
    asyncio.run(test_service())

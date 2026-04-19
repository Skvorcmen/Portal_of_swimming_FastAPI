import asyncio

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.database import async_session_maker
from app.models import UserRole
from app.services.auth_service import AuthService


async def test_service():
    async with async_session_maker() as session:
        service = AuthService(session)

        print("1. Регистрация нового пользователя...")
        try:
            user = await service.register_user(
                email="service@test.com",
                username="serviceuser",
                password="123",
                full_name="Service User",
                role=UserRole.ATHLETE,
            )
            print(f"   ✅ Зарегистрирован: {user.username} (id={user.id})")
        except UserAlreadyExistsError as e:
            print(f"   ⚠️ Уже есть: {e}")

        print("\n2. Логин...")
        try:
            token = await service.login_user("serviceuser", "123")
            print(f"   ✅ Токен получен: {token[:50]}...")
        except InvalidCredentialsError as e:
            print(f"   ❌ Ошибка: {e}")

        print("\n3. Логин с неверным паролем...")
        try:
            await service.login_user("serviceuser", "wrongpassword")
        except InvalidCredentialsError:
            print("   ✅ Ожидаемая ошибка: неверные учётные данные")


if __name__ == "__main__":
    asyncio.run(test_service())

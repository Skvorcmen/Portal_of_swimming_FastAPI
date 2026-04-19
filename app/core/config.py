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

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Создаём один экземпляр настроек для всего приложения
settings = Settings()

# AI-generated: настройки приложения из переменных окружения / .env
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./data/moment.db"
    admin_api_key: str = "dev-admin-key-change-me"


@lru_cache
def get_settings() -> Settings:
    return Settings()

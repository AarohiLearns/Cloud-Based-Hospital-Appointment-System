from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Hospital Appointment System"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    database_url: str = "sqlite+aiosqlite:///./hospital.db"
    auto_create_tables: bool = True  # switch to migrations (Alembic) before production

    jwt_secret: str = "dev-only-secret-change-me-before-deploying-0123456789"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    clinic_timezone: str = "Asia/Kolkata"
    max_booking_days_ahead: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

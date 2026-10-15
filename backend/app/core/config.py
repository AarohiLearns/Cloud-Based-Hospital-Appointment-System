import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Hospital Appointment System"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str | list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://main.dlyy1mwq0e0yu.amplifyapp.com",
        "*",
    ]

    @field_validator("cors_origins", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    database_url: str = "sqlite+aiosqlite:///./hospital.db"
    auto_create_tables: bool = True  # switch to migrations (Alembic) before production

    jwt_secret: str = "REPLACE_WITH_ENV_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    clinic_timezone: str = "Asia/Kolkata"
    max_booking_days_ahead: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

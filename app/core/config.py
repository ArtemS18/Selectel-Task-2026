from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/postgres", # оставил бд по умолчанию postgres
        validation_alias="DATABASE_URL", # исправил опечатку в алиасе
    )
    log_level: Literal["INFO", "DEBUG"] = "INFO"
    parse_schedule_minutes: int = 5


settings = Settings()


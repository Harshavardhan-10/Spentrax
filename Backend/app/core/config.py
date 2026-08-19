"""Application configuration loaded from environment variables.

All configuration is environment driven (see .env.example). Secrets such as
SECRET_KEY and AI_API_KEY are read from the environment and are never
hard-coded or exposed to the frontend.
"""
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Smart Expense & Budget Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./expense.db"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI provider abstraction
    AI_PROVIDER: str = "rule_based"  # openai | rule_based
    AI_API_KEY: str = ""
    AI_MODEL: str = ""
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_TIMEOUT_SECONDS: int = 15

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Uploads
    MAX_CSV_SIZE_MB: int = 5

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def default_if_empty(cls, value):
        # Hosts (e.g. Render) may inject DATABASE_URL as an empty string when it
        # was left unset; fall back to local SQLite instead of crashing
        # SQLAlchemy with an empty URL.
        if value is None or (isinstance(value, str) and not value.strip()):
            return "sqlite:///./expense.db"
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

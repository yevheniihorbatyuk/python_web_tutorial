"""
Application configuration via environment variables.
Extends the Module 12 Settings pattern with email, Cloudinary, and Redis.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Contacts API"
    DEBUG: bool = False

    # Database (same as Module 12)
    DATABASE_URL: str = "sqlite+aiosqlite:///./contacts.db"

    # JWT (same as Module 12)
    JWT_SECRET_KEY: str = "change-this-secret"
    JWT_REFRESH_SECRET: str = "change-this-refresh-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email verification token
    # Separate secret from JWT so tokens are not interchangeable
    EMAIL_TOKEN_SECRET: str = "change-this-email-secret"
    EMAIL_TOKEN_EXPIRE_HOURS: int = 24

    # SMTP
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = "noreply@example.com"
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@example.com"
    SMTP_FROM_NAME: str = "Contacts App"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = "demo"
    CLOUDINARY_API_KEY: str = "demo"
    CLOUDINARY_API_SECRET: str = "demo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

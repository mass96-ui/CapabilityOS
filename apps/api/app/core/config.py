from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    All configuration values are loaded from environment variables
    and validated using Pydantic Settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================
    # Application
    # ============================================================

    APP_NAME: str = Field(default="CapabilityOS API")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # ============================================================
    # Security
    # ============================================================

    SECRET_KEY: str = Field(
        default="CHANGE_THIS_IN_PRODUCTION"
    )

    JWT_SECRET_KEY: str = Field(
        default="CHANGE_THIS_IN_PRODUCTION"
    )

    JWT_ALGORITHM: str = Field(default="HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)

    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(default=30)
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = Field(default=48)
    EMAIL_VERIFICATION_OTP_EXPIRE_MINUTES: int = Field(default=10)

    # ============================================================
    # Database
    # ============================================================

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./capabilityos.db"
    )

    # ============================================================
    # Redis
    # ============================================================

    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # ============================================================
    # Email
    # ============================================================

    SMTP_HOST: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=1025)
    SMTP_USERNAME: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_TLS: bool = Field(default=True)

    # ============================================================
    # CORS
    # ============================================================

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001"
    )

    TRUSTED_HOSTS: str = Field(
        default="localhost,127.0.0.1,testserver,*"
    )

    # ============================================================
    # Logging
    # ============================================================

    LOG_LEVEL: str = Field(default="INFO")

    # ============================================================
    # Rate Limiting
    # ============================================================

    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)

    # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def cors_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def trusted_hosts(self) -> List[str]:
        return [
            host.strip()
            for host in self.TRUSTED_HOSTS.split(",")
            if host.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached Settings instance.

    Ensures the configuration is loaded only once
    during the application lifecycle.
    """
    return Settings()


settings = get_settings()
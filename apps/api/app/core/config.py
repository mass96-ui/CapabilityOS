from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = Field(default="CapabilityOS API")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    SECRET_KEY: str = Field(default="")
    JWT_SECRET_KEY: str = Field(default="")
    JWT_ALGORITHM: str = Field(default="HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)
    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(default=30)
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = Field(default=48)
    EMAIL_VERIFICATION_OTP_EXPIRE_MINUTES: int = Field(default=10)

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./capabilityos.db"
    )

    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    SMTP_HOST: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=1025)
    SMTP_USERNAME: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_TLS: bool = Field(default=True)

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001"
    )

    TRUSTED_HOSTS: str = Field(
        default="localhost,127.0.0.1,testserver"
    )

    LOG_LEVEL: str = Field(default="INFO")

    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() != "production":
            return self

        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be set to a strong value in production."
            )

        if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong value in production."
            )

        if self.DEBUG:
            raise ValueError("DEBUG must be false in production.")

        origins = self.cors_origins
        if not origins:
            raise ValueError(
                "CORS_ORIGINS must be explicitly configured in production."
            )

        if "*" in origins:
            raise ValueError(
                "CORS_ORIGINS must not contain '*' in production."
            )

        if any(not origin.startswith("https://") for origin in origins):
            raise ValueError(
                "Production CORS origins must use HTTPS."
            )

        hosts = self.trusted_hosts
        if not hosts:
            raise ValueError(
                "TRUSTED_HOSTS must be explicitly configured in production."
            )

        if "*" in hosts:
            raise ValueError(
                "TRUSTED_HOSTS must not contain '*' in production."
            )

        if any("://" in host for host in hosts):
            raise ValueError(
                "TRUSTED_HOSTS must contain hostnames, not URLs."
            )

        return self

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
    return Settings()


settings = get_settings()

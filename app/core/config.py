"""Application settings loaded from environment variables / `.env` file."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application configuration.

    Values are read from the process environment first, then from a local
    `.env` file. Required settings intentionally have no default so that a
    misconfigured deployment fails loudly at import time instead of silently
    running with an insecure or unusable value.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Database ---------------------------------------------------------
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string, e.g. postgresql://user:pass@host:5432/db",
    )

    # --- Security ---------------------------------------------------------
    SECRET_KEY: str = Field(
        ...,
        description="Secret key used to sign and verify JWT access tokens.",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        gt=0,
        description="Access token lifetime, in minutes.",
    )

    # --- Application ------------------------------------------------------
    APP_NAME: str = Field(default="Job Application Tracker API")
    APP_VERSION: str = Field(default="1.0.0")
    API_V1_PREFIX: str = Field(default="")
    ENV: str = Field(default="development", description="development | testing | production")
    DEBUG: bool = Field(default=False, description="Log every SQL statement issued by SQLAlchemy.")

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of origins allowed by CORS middleware.",
    )

    @field_validator("ENV", mode="before")
    @classmethod
    def _normalize_env(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("SECRET_KEY must not be empty.")
        if cleaned == "your_super_secret_key_here":
            raise ValueError(
                "SECRET_KEY still holds the placeholder value from .env.example. "
                "Generate a real key with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
        return cleaned

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Normalized SQLAlchemy connection string.

        Render and other PaaS providers frequently hand out ``postgres://`` or
        ``postgresql://`` URLs, which SQLAlchemy does not accept directly. This
        pins the driver to psycopg2 so migrations and the app always agree.

        A bare DSN (``user:pass@host:5432/db``) also gets the driver prefix. A
        URL that already carries an explicit scheme or driver is returned
        unchanged.
        """
        url = self.DATABASE_URL.strip()
        if not url:
            raise ValueError("DATABASE_URL must not be empty.")

        if "://" not in url:
            return f"postgresql+psycopg2://{url}"

        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return url.replace(prefix, "postgresql+psycopg2://", 1)

        return url

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins as a clean list of non-empty origin strings."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of :class:`Settings`.

    Cached so the `.env` file is read once per process rather than on every
    request.
    """
    return Settings()

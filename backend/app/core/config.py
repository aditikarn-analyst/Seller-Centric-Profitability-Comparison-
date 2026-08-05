"""Application configuration.

All runtime configuration is read from environment variables (or a local ``.env``
file) via Pydantic Settings, so nothing environment-specific — database URLs,
secrets, token lifetimes — is ever hard-coded in the source (README §10).

Import the singleton ``settings`` anywhere it is needed::

    from app.core.config import settings
    engine = create_engine(settings.database_url)
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings, validated at startup.

    Field names are lower_snake_case; the corresponding environment variables
    are matched case-insensitively (``DATABASE_URL`` -> ``database_url``).
    A missing required value or a wrong type fails fast at import time rather
    than surfacing as a confusing error deep in a request.
    """

    # Application
    app_name: str = "Marketplace Profitability Analyzer"
    environment: Literal["development", "production"] = "development"

    # Database (SQLite in dev, PostgreSQL in prod — README §10)
    database_url: str = "sqlite:///./app.db"

    # Auth (README §10)
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton.

    ``lru_cache`` guarantees the ``.env`` file is parsed exactly once per
    process and that every module shares one immutable settings object.
    """
    return Settings()


settings = get_settings()

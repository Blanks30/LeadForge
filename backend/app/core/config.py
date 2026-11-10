"""Application settings and environment configuration."""

import json
from contextlib import suppress
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory paths
CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
BACKEND_DIR = APP_DIR.parent
DEFAULT_DATA_DIR = BACKEND_DIR / "data"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "leadforge.db"


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""

    ENVIRONMENT: str = Field(
        default="development",
        description="Application runtime environment (development, staging, production)",
    )
    USE_MOCK_APIS: bool = Field(
        default=True,
        description="Enable offline mock providers (default for hackathon/dev)",
    )

    TINYFISH_API_KEY: str = Field(
        default="",
        description="TinyFish API Key",
    )
    TAVILY_API_KEY: str = Field(
        default="",
        description="Tavily Search API Key for general-purpose internet search",
    )
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API Key",
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Configurable Gemini model ID",
    )

    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}",
        description="SQLAlchemy async SQLite database connection string",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Normalize PostgreSQL connection strings to use asyncpg driver."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://") and not v.startswith("postgresql+"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    CORS_ORIGINS: list[str] | str = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins for local frontend",
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: list[str] | str) -> list[str]:
        """Support both JSON list format and comma-separated string format."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                with suppress(json.JSONDecodeError, ValueError):
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [
                            str(origin).strip()
                            for origin in parsed
                            if str(origin).strip()
                        ]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return [str(origin).strip() for origin in v if str(origin).strip()]

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

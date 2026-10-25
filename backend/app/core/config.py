"""Application settings and environment configuration."""

from pathlib import Path

from pydantic import Field
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
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API Key",
    )
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Configurable Gemini model ID",
    )

    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}",
        description="SQLAlchemy async SQLite database connection string",
    )

    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins for local frontend",
    )

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

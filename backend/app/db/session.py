"""Async database engine, session management, and SQLite initialization.

Configures SQLite WAL mode, foreign key enforcement, and pragmas
according to DATABASE.md specifications.
"""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.models import Base


def configure_sqlite_pragmas(sync_engine: Engine) -> None:
    """Attach SQLite pragma configuration listeners to sync engine."""

    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.execute("PRAGMA cache_size = -64000")
        cursor.close()


# Primary async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

configure_sqlite_pragmas(engine.sync_engine)

# Async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db(target_engine: AsyncEngine | None = None) -> None:
    """Initialize database tables and indexes idempotently.

    Executes CREATE TABLE IF NOT EXISTS and index creation defined in Base metadata.
    Ensures target directory exists when using file-based SQLite.
    """
    eng = target_engine or engine
    db_name = eng.url.database

    if db_name and db_name != ":memory:":
        db_path = Path(db_name)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migrate any missing columns for existing SQLite tables (e.g., generation_source)
        # Using PRAGMA table_info check avoids transaction errors on nested/savepoint operations
        result = await conn.execute(text("PRAGMA table_info(outreach_drafts)"))
        existing_cols = {row[1] for row in result.fetchall()}
        if "generation_source" not in existing_cols:
            await conn.execute(
                text(
                    "ALTER TABLE outreach_drafts ADD COLUMN generation_source TEXT NOT NULL DEFAULT 'DETERMINISTIC_TEMPLATE'"
                )
            )


async def check_db_health(target_engine: AsyncEngine | None = None) -> bool:
    """Verify database connectivity by executing a lightweight query."""
    eng = target_engine or engine
    try:
        async with eng.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except (SQLAlchemyError, OSError):
        return False

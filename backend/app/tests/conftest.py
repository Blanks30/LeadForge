"""Pytest fixtures and environment configuration for LeadForge backend testing.

CRITICAL INVARIANT:
Tests must NEVER read from or write to `backend/data/leadforge.db`.
All tests run against isolated, temporary databases that are wiped clean
between test cases and destroyed at session end.
"""

import contextlib
import os
import sqlite3
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Strict Test Database Isolation Guard
# ---------------------------------------------------------------------------
# Before any application module is loaded, point DATABASE_URL to an isolated
# temporary SQLite file. Under no circumstances may any test write to
# backend/data/leadforge.db.
# ---------------------------------------------------------------------------
_TEST_TEMP_DIR = tempfile.TemporaryDirectory(
    prefix="leadforge_test_db_", ignore_cleanup_errors=True
)
_ISOLATED_TEST_DB_PATH = Path(_TEST_TEMP_DIR.name) / "test_isolated.db"
_ISOLATED_TEST_DB_URL = f"sqlite+aiosqlite:///{_ISOLATED_TEST_DB_PATH.as_posix()}"

# Enforce environment variable for settings instantiation
os.environ["DATABASE_URL"] = _ISOLATED_TEST_DB_URL

# Import application settings and verify URL isolation
from app.core.config import settings
from app.db.models import Base
from app.db.session import (
    configure_sqlite_pragmas,
)
from app.db.session import (
    engine as app_engine,
)

# Overwrite in-memory settings to guarantee isolation even if config was previously imported
settings.DATABASE_URL = _ISOLATED_TEST_DB_URL


@pytest.fixture(autouse=True)
def enforce_test_db_isolation():
    """Guarantee database isolation before and after each test case.

    Ensures:
    1. The application engine never points to the real `leadforge.db`.
    2. Tables in the isolated test database are purged between tests to prevent
       cross-test contamination and test-order dependencies.
    """
    # Safety assertion: verify application engine is never pointing to real DB
    db_name = str(app_engine.url.database or "")
    assert "leadforge.db" not in db_name, (
        f"CRITICAL VIOLATION: Application engine is pointing to production database: {db_name}"
    )

    yield

    # Clean tables in the temporary database after each test
    if _ISOLATED_TEST_DB_PATH.exists():
        with contextlib.suppress(sqlite3.OperationalError):
            conn = sqlite3.connect(_ISOLATED_TEST_DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
            for t in tables:
                cur.execute(f"DELETE FROM {t}")
            conn.commit()
            conn.close()


def pytest_sessionfinish(session, exitstatus):
    """Dispose engines and clean up temporary test database directory."""
    with contextlib.suppress(SQLAlchemyError, OSError):
        app_engine.sync_engine.dispose()
    with contextlib.suppress(OSError):
        _TEST_TEMP_DIR.cleanup()


@pytest_asyncio.fixture
async def test_engine() -> AsyncIterator[AsyncEngine]:
    """Create an isolated in-memory SQLite async engine with StaticPool."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
        future=True,
    )
    configure_sqlite_pragmas(engine.sync_engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Provide an async session bound to the in-memory test engine."""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

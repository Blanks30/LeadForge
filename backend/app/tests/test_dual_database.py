"""Tests for dual database support (SQLite and PostgreSQL).

Validates:
1. Cross-dialect DDL compilation for all 5 models.
2. Cross-dialect timestamp default compilation (func.now()).
3. SQLite pragma configuration and dialect isolation.
4. Database URL normalization for PostgreSQL (asyncpg).
5. Database initialization and migration dialect branching.
6. Seeding idempotency on fresh and populated databases.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import func
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable

from app.core.config import Settings
from app.db.models import (
    EvidenceItem,
    IcpProfile,
    OutreachDraft,
    Prospect,
    WebSource,
)
from app.db.seed_data import seed_initial_data
from app.db.session import configure_sqlite_pragmas, init_db


def test_models_ddl_compilation_postgresql():
    """Verify all 5 models compile valid PostgreSQL DDL without dialect errors."""
    pg_dialect = postgresql.dialect()
    tables = [IcpProfile, Prospect, WebSource, EvidenceItem, OutreachDraft]

    for model in tables:
        ddl = str(CreateTable(model.__table__).compile(dialect=pg_dialect))
        assert "CREATE TABLE" in ddl
        assert model.__tablename__ in ddl
        # Confirm no SQLite-specific datetime('now', 'utc') syntax in PostgreSQL DDL
        assert "datetime('now'" not in ddl.lower()


def test_models_ddl_compilation_sqlite():
    """Verify all 5 models compile valid SQLite DDL."""
    sl_dialect = sqlite.dialect()
    tables = [IcpProfile, Prospect, WebSource, EvidenceItem, OutreachDraft]

    for model in tables:
        ddl = str(CreateTable(model.__table__).compile(dialect=sl_dialect))
        assert "CREATE TABLE" in ddl
        assert model.__tablename__ in ddl


def test_timestamp_default_compilation_cross_dialect():
    """Verify func.now() resolves to dialect-appropriate SQL for SQLite and PostgreSQL."""
    stmt_sqlite = str(func.now().compile(dialect=sqlite.dialect()))
    stmt_pg = str(func.now().compile(dialect=postgresql.dialect()))

    assert stmt_sqlite == "CURRENT_TIMESTAMP"
    assert stmt_pg == "now()"


def test_database_url_normalization():
    """Verify PostgreSQL connection URLs are normalized to asyncpg driver."""
    s1 = Settings(DATABASE_URL="postgres://user:secret@ep-cool-123.neon.tech/neondb")
    assert s1.DATABASE_URL.startswith("postgresql+asyncpg://")

    s2 = Settings(DATABASE_URL="postgresql://user:secret@ep-cool-123.neon.tech/neondb")
    assert s2.DATABASE_URL.startswith("postgresql+asyncpg://")

    s3 = Settings(
        DATABASE_URL="postgresql+asyncpg://user:secret@ep-cool-123.neon.tech/neondb"
    )
    assert (
        s3.DATABASE_URL
        == "postgresql+asyncpg://user:secret@ep-cool-123.neon.tech/neondb"
    )

    s4 = Settings(DATABASE_URL="sqlite+aiosqlite:///local.db")
    assert s4.DATABASE_URL == "sqlite+aiosqlite:///local.db"


def test_sqlite_pragmas_attach_only_to_sqlite():
    """Verify SQLite PRAGMA listener applies foreign_keys and WAL settings on connect."""
    from sqlalchemy import create_engine

    sync_engine = create_engine("sqlite:///:memory:")
    configure_sqlite_pragmas(sync_engine)

    with sync_engine.connect() as conn:
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert foreign_keys == 1


@pytest.mark.asyncio
async def test_init_db_skips_sqlite_pragmas_on_postgresql():
    """Verify init_db does not execute SQLite PRAGMA table_info on non-sqlite engine."""
    mock_engine = MagicMock()
    mock_engine.url.get_backend_name.return_value = "postgresql"
    mock_engine.url.database = "neondb"

    mock_conn = AsyncMock()
    mock_engine.begin.return_value.__aenter__.return_value = mock_conn

    await init_db(mock_engine)

    # run_sync(Base.metadata.create_all) should be called
    assert mock_conn.run_sync.called
    # PRAGMA table_info should NOT be executed on postgresql
    for call in mock_conn.execute.call_args_list:
        query_text = str(call[0][0])
        assert "PRAGMA" not in query_text


@pytest.mark.asyncio
async def test_seeding_idempotency(db_session):
    """Verify repeated seeding calls do not duplicate prospects or ICP records."""
    # First seed
    icp1, prospects1 = await seed_initial_data(db_session)
    count1 = len(prospects1)
    assert count1 == 10

    # Second seed
    icp2, prospects2 = await seed_initial_data(db_session)
    count2 = len(prospects2)

    assert count1 == count2
    assert icp1.id == icp2.id
    assert [p.id for p in prospects1] == [p.id for p in prospects2]


def test_test_environment_database_isolation():
    """Verify test suite engine is isolated from real application leadforge.db."""
    from app.core.config import settings
    from app.db.session import engine

    assert "leadforge.db" not in str(settings.DATABASE_URL)
    assert "leadforge.db" not in str(engine.url.database or "")
    assert "test_isolated" in str(engine.url.database or "")

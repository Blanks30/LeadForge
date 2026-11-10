"""Tests for database migrations and schema evolution safety.

Verifies:
1. Migration of legacy database containing outreach drafts without generation_source column.
2. Existing records and their data are strictly preserved.
3. Multiple successive executions of init_db() are idempotent and error-free.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.session import init_db


@pytest.mark.asyncio
async def test_migration_adds_generation_source_to_legacy_db():
    """Verify migrating an existing database that has an outreach_drafts table missing generation_source."""
    legacy_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # 1. Create a legacy schema without generation_source
    async with legacy_engine.begin() as conn:
        await conn.execute(
            text("""
            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                domain TEXT NOT NULL UNIQUE,
                lead_score INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        )
        await conn.execute(
            text("""
            CREATE TABLE outreach_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                template_type TEXT NOT NULL DEFAULT 'EVIDENCE_PROBLEM_SOLUTION',
                subject_line TEXT NOT NULL,
                body_text TEXT NOT NULL,
                citations_json TEXT NOT NULL,
                tone TEXT NOT NULL DEFAULT 'CONSULTATIVE_DIRECT',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        )
        # Seed a prospect and an outreach draft in the legacy schema
        await conn.execute(
            text("""
            INSERT INTO prospects (id, company_name, website_url, domain)
            VALUES (1, 'LegacyCo', 'https://legacy.co', 'legacy.co')
        """)
        )
        await conn.execute(
            text("""
            INSERT INTO outreach_drafts (id, prospect_id, subject_line, body_text, citations_json)
            VALUES (1, 1, 'Legacy Subject', 'Legacy Body [Ref: #1]', '[1]')
        """)
        )

    # 2. Run init_db() on this legacy database
    await init_db(legacy_engine)

    # 3. Verify column was added and existing record preserved with the default value
    async with legacy_engine.connect() as conn:
        res = await conn.execute(text("PRAGMA table_info(outreach_drafts)"))
        cols = {row[1] for row in res.fetchall()}
        assert "generation_source" in cols

        # Check existing row
        row = (
            await conn.execute(
                text(
                    "SELECT id, subject_line, generation_source FROM outreach_drafts WHERE id = 1"
                )
            )
        ).fetchone()
        assert row is not None
        assert row[0] == 1
        assert row[1] == "Legacy Subject"
        assert row[2] == "DETERMINISTIC_TEMPLATE"

    # 4. Verify idempotent execution (run init_db again without error)
    await init_db(legacy_engine)
    await init_db(legacy_engine)

    await legacy_engine.dispose()

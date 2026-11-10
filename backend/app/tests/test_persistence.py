"""Tests verifying database persistence across engine/session restarts.

Ensures:
1. Prospect, EvidenceItem, and OutreachDraft entities written to disk persist across session closures.
2. Changes survive engine disposal and re-initialization without data loss or corruption.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.models import Base, EvidenceItem, IcpProfile, OutreachDraft, Prospect


@pytest.mark.asyncio
async def test_persistence_across_connection_cycles(tmp_path):
    """Verify that records persist across distinct engine lifecycles when using file SQLite."""
    db_file = tmp_path / "test_persistence.db"
    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"

    # Cycle 1: Initialize database, insert records, and commit
    engine_1 = create_async_engine(db_url)
    async with engine_1.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine_1) as session:
        icp = IcpProfile(vertical="Indian SMB Accounting")
        session.add(icp)
        await session.flush()

        prospect = Prospect(
            icp_id=icp.id,
            company_name="FloBiz / myBillBook",
            website_url="https://mybillbook.in",
            domain="mybillbook.in",
            lead_score=90,
            status="ANALYZED",
        )
        session.add(prospect)
        await session.flush()

        evidence = EvidenceItem(
            prospect_id=prospect.id,
            category="SMB_FOCUS",
            claim_text="Provides mobile GST invoicing",
            exact_quote="India's leading GST billing software",
            epistemic_status="FACT",
        )
        draft = OutreachDraft(
            prospect_id=prospect.id,
            subject_line="GST Invoicing for SMEs",
            body_text="Hi FloBiz team [Ref: #1]",
            citations_json="[1]",
            generation_source="GEMINI_AI",
        )
        session.add_all([evidence, draft])
        await session.commit()

    # Completely dispose first engine simulating process exit
    await engine_1.dispose()

    # Cycle 2: Launch fresh engine against the same file on disk
    engine_2 = create_async_engine(db_url)
    async with AsyncSession(engine_2) as session:
        q_prospect = await session.execute(
            select(Prospect).where(Prospect.domain == "mybillbook.in")
        )
        loaded_prospect = q_prospect.scalar_one_or_none()

        assert loaded_prospect is not None
        assert loaded_prospect.company_name == "FloBiz / myBillBook"
        assert loaded_prospect.lead_score == 90
        assert loaded_prospect.status == "ANALYZED"

        # Check related evidence items and drafts
        assert len(loaded_prospect.evidence_items) == 1
        assert loaded_prospect.evidence_items[0].epistemic_status == "FACT"
        assert (
            loaded_prospect.evidence_items[0].exact_quote
            == "India's leading GST billing software"
        )

        assert len(loaded_prospect.outreach_drafts) == 1
        assert loaded_prospect.outreach_drafts[0].generation_source == "GEMINI_AI"

    await engine_2.dispose()

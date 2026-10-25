"""Tests for database connectivity, pragmas, schema constraints, and models."""

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.db.models import (
    EvidenceItem,
    IcpProfile,
    OutreachDraft,
    Prospect,
    WebSource,
)
from app.db.session import check_db_health, init_db


@pytest.mark.asyncio
async def test_sqlite_pragmas_configured(test_engine: AsyncEngine) -> None:
    """Verify that foreign keys and busy timeout pragmas are active."""
    async with test_engine.connect() as conn:
        fk_res = await conn.execute(text("PRAGMA foreign_keys"))
        assert fk_res.scalar() == 1

        timeout_res = await conn.execute(text("PRAGMA busy_timeout"))
        assert timeout_res.scalar() == 5000


@pytest.mark.asyncio
async def test_all_five_tables_created(test_engine: AsyncEngine) -> None:
    """Verify that all five core tables exist in the database."""
    async with test_engine.connect() as conn:
        table_names = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

    expected_tables = {
        "icp_profiles",
        "prospects",
        "web_sources",
        "evidence_items",
        "outreach_drafts",
    }
    assert expected_tables.issubset(set(table_names))


@pytest.mark.asyncio
async def test_idempotent_init_db(test_engine: AsyncEngine) -> None:
    """Verify that calling init_db repeatedly does not raise errors."""
    await init_db(test_engine)
    await init_db(test_engine)

    healthy = await check_db_health(test_engine)
    assert healthy is True


@pytest.mark.asyncio
async def test_full_model_relationships_and_defaults(
    db_session: AsyncSession,
) -> None:
    """Verify entity creation and relational traversal across all models."""
    # 1. Create ICP Profile
    icp = IcpProfile(
        vertical="B2B SaaS serving SMBs / MSMEs",
        target_geo="India",
    )
    db_session.add(icp)
    await db_session.commit()
    await db_session.refresh(icp)
    assert icp.id is not None
    assert "Self-serve onboarding" in icp.smb_criteria_json

    # 2. Create Prospect
    prospect = Prospect(
        icp_id=icp.id,
        company_name="Khatabook",
        website_url="https://khatabook.com",
        domain="khatabook.com",
        lead_score=85,
        status="ANALYZED",
    )
    db_session.add(prospect)
    await db_session.commit()
    await db_session.refresh(prospect)
    assert prospect.id is not None
    assert prospect.lead_score == 85

    # 3. Create WebSource
    source = WebSource(
        prospect_id=prospect.id,
        url="https://khatabook.com/pricing",
        page_type="PRICING",
        raw_text_snippet="Starter plan: ₹499/month billed annually.",
        content_hash="sha256_dummy_hash_for_testing",
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    assert source.id is not None
    assert source.http_status == 200

    # 4. Create EvidenceItem
    evidence = EvidenceItem(
        prospect_id=prospect.id,
        source_id=source.id,
        category="SMB_FOCUS",
        rubric_criterion="INR_PRICING",
        claim_text="Starter plan priced at ₹499 per month for small retailers.",
        exact_quote="Starter plan: ₹499/month billed annually.",
        epistemic_status="FACT",
        confidence_score=1.0,
    )
    db_session.add(evidence)
    await db_session.commit()
    await db_session.refresh(evidence)
    assert evidence.id is not None
    assert evidence.epistemic_status == "FACT"

    # 5. Create OutreachDraft
    draft = OutreachDraft(
        prospect_id=prospect.id,
        subject_line="Empowering Indian SMB retailers with Khatabook",
        body_text="Noticed your starter plan is priced at ₹499/month [Ref: #1].",
        citations_json=f"[{evidence.id}]",
    )
    db_session.add(draft)
    await db_session.commit()
    await db_session.refresh(draft)
    assert draft.id is not None
    assert draft.template_type == "EVIDENCE_PROBLEM_SOLUTION"

    target_prospect_id = prospect.id
    target_icp_id = icp.id

    # Expunge in-memory tracked objects to guarantee fresh database query
    db_session.expunge_all()

    # Query back via Prospect and test relationship navigation
    query = select(Prospect).where(Prospect.id == target_prospect_id)
    result = await db_session.execute(query)
    fetched_prospect = result.scalar_one()

    assert fetched_prospect.icp.id == target_icp_id
    assert len(fetched_prospect.web_sources) == 1
    assert len(fetched_prospect.evidence_items) == 1
    assert len(fetched_prospect.outreach_drafts) == 1
    assert fetched_prospect.web_sources[0].url == "https://khatabook.com/pricing"
    assert fetched_prospect.evidence_items[0].rubric_criterion == "INR_PRICING"
    assert fetched_prospect.evidence_items[0].source is not None
    assert (
        fetched_prospect.evidence_items[0].source.url == "https://khatabook.com/pricing"
    )


@pytest.mark.asyncio
async def test_foreign_key_restricts_icp_deletion(db_session: AsyncSession) -> None:
    """Verify that deleting an ICP profile referenced by a Prospect raises IntegrityError."""
    icp = IcpProfile(vertical="FinTech SaaS")
    db_session.add(icp)
    await db_session.commit()
    await db_session.refresh(icp)

    prospect = Prospect(
        icp_id=icp.id,
        company_name="Vyapar",
        website_url="https://vyaparapp.in",
        domain="vyaparapp.in",
    )
    db_session.add(prospect)
    await db_session.commit()

    # Attempting to delete icp should fail with IntegrityError (RESTRICT)
    await db_session.delete(icp)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cascade_deletes_when_prospect_removed(
    db_session: AsyncSession,
) -> None:
    """Verify that deleting a prospect cascades to web_sources, evidence, and drafts."""
    icp = IcpProfile(vertical="SME ERP")
    db_session.add(icp)
    await db_session.commit()
    await db_session.refresh(icp)

    prospect = Prospect(
        icp_id=icp.id,
        company_name="myBillBook",
        website_url="https://mybillbook.in",
        domain="mybillbook.in",
    )
    db_session.add(prospect)
    await db_session.commit()
    await db_session.refresh(prospect)

    source = WebSource(
        prospect_id=prospect.id,
        url="https://mybillbook.in/about",
        raw_text_snippet="GST billing for Indian SME traders.",
        content_hash="hash_mybillbook",
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)

    evidence = EvidenceItem(
        prospect_id=prospect.id,
        source_id=source.id,
        category="SMB_FOCUS",
        claim_text="Provides GST billing app",
        epistemic_status="FACT",
    )
    draft = OutreachDraft(
        prospect_id=prospect.id,
        subject_line="GST billing expansion",
        body_text="Hello FloBiz team",
        citations_json="[]",
    )
    db_session.add_all([evidence, draft])
    await db_session.commit()

    # Delete prospect
    await db_session.delete(prospect)
    await db_session.commit()

    # Assert children are gone
    remaining_sources = await db_session.execute(
        select(WebSource).where(WebSource.prospect_id == prospect.id)
    )
    remaining_evidence = await db_session.execute(
        select(EvidenceItem).where(EvidenceItem.prospect_id == prospect.id)
    )
    remaining_drafts = await db_session.execute(
        select(OutreachDraft).where(OutreachDraft.prospect_id == prospect.id)
    )

    assert remaining_sources.scalars().all() == []
    assert remaining_evidence.scalars().all() == []
    assert remaining_drafts.scalars().all() == []


@pytest.mark.asyncio
async def test_check_constraint_lead_score_range(db_session: AsyncSession) -> None:
    """Verify that lead_score outside 0..100 violates CHECK constraint."""
    icp = IcpProfile()
    db_session.add(icp)
    await db_session.commit()
    await db_session.refresh(icp)

    invalid_prospect = Prospect(
        icp_id=icp.id,
        company_name="OverScore SaaS",
        website_url="https://overscore.io",
        domain="overscore.io",
        lead_score=105,  # Exceeds max 100
    )
    db_session.add(invalid_prospect)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_check_constraint_epistemic_status_valid(
    db_session: AsyncSession,
) -> None:
    """Verify that invalid epistemic status violates CHECK constraint."""
    icp = IcpProfile()
    db_session.add(icp)
    await db_session.commit()
    await db_session.refresh(icp)

    prospect = Prospect(
        icp_id=icp.id,
        company_name="Dukaan",
        website_url="https://mydukaan.io",
        domain="mydukaan.io",
    )
    db_session.add(prospect)
    await db_session.commit()
    await db_session.refresh(prospect)

    invalid_evidence = EvidenceItem(
        prospect_id=prospect.id,
        category="TECH_FIT",
        claim_text="Unverified assertion",
        epistemic_status="GUESS",  # Invalid! Must be FACT, INFERENCE, or UNKNOWN
    )
    db_session.add(invalid_evidence)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

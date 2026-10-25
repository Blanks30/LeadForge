"""Tests for seed data idempotency and Pydantic schema validation."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IcpProfile, Prospect
from app.db.seed_data import SAMPLE_COMPANIES, seed_initial_data
from app.schemas.icp_schema import IcpResponse
from app.schemas.prospect_schema import (
    ProspectDetailSchema,
    ProspectSummarySchema,
)


@pytest.mark.asyncio
async def test_successful_initial_seeding(db_session: AsyncSession) -> None:
    """Verify that initial seeding creates 1 ICP and exactly 10 prospects."""
    icp, prospects = await seed_initial_data(db_session)

    assert icp.id is not None
    assert icp.vertical == "B2B SaaS serving SMBs / MSMEs"
    assert icp.target_geo == "India"
    assert len(prospects) == 10

    # Verify all 10 target domains are seeded
    seeded_domains = {p.domain for p in prospects}
    expected_domains = {c["domain"] for c in SAMPLE_COMPANIES}
    assert seeded_domains == expected_domains

    # Verify seed properties adhere to unresearched demo standard
    for p in prospects:
        assert p.status == "PENDING"
        assert p.lead_score == 0
        assert p.score_breakdown_json is None
        assert p.researched_at is None
        assert p.icp_id == icp.id


@pytest.mark.asyncio
async def test_repeated_seeding_is_idempotent(db_session: AsyncSession) -> None:
    """Verify running seed_initial_data multiple times produces no duplicates."""
    # First seeding
    await seed_initial_data(db_session)

    # Second seeding
    icp_second, prospects_second = await seed_initial_data(db_session)

    assert icp_second.id is not None
    assert len(prospects_second) == 10

    # Check total database counts directly via SELECT COUNT(*)
    prospect_count_query = select(func.count(Prospect.id))
    icp_count_query = select(func.count(IcpProfile.id))

    prospect_count = (await db_session.execute(prospect_count_query)).scalar()
    icp_count = (await db_session.execute(icp_count_query)).scalar()

    assert prospect_count == 10
    assert icp_count == 1


@pytest.mark.asyncio
async def test_pydantic_icp_serialization(db_session: AsyncSession) -> None:
    """Verify IcpResponse cleanly serializes from SQLAlchemy IcpProfile ORM instance."""
    icp, _ = await seed_initial_data(db_session)

    dto = IcpResponse.model_validate(icp)

    assert dto.id == icp.id
    assert dto.vertical == "B2B SaaS serving SMBs / MSMEs"
    assert isinstance(dto.smb_criteria, list)
    assert len(dto.smb_criteria) == 4
    assert "Pricing in INR" in dto.smb_criteria
    assert isinstance(dto.tech_keywords, list)
    assert len(dto.tech_keywords) == 8
    assert "kirana" in dto.tech_keywords


@pytest.mark.asyncio
async def test_pydantic_prospect_summary_serialization(
    db_session: AsyncSession,
) -> None:
    """Verify ProspectSummarySchema serialization from SQLAlchemy Prospect model."""
    _, prospects = await seed_initial_data(db_session)
    khatabook = next(p for p in prospects if p.domain == "khatabook.com")

    dto = ProspectSummarySchema.model_validate(khatabook)

    assert dto.id == khatabook.id
    assert dto.company_name == "Khatabook"
    assert dto.domain == "khatabook.com"
    assert dto.website_url == "https://khatabook.com"
    assert dto.status == "PENDING"
    assert dto.lead_score == 0


@pytest.mark.asyncio
async def test_pydantic_prospect_detail_with_score_breakdown(
    db_session: AsyncSession,
) -> None:
    """Verify ProspectDetailSchema parses JSON score breakdown and relations."""
    _, prospects = await seed_initial_data(db_session)
    prospect = prospects[0]

    # Assign synthetic breakdown for serialization check
    prospect.score_breakdown_json = (
        '{"smb_focus": 35, "saas_model": 25, "growth": 15, "evidence": 10}'
    )
    prospect.lead_score = 85
    prospect.status = "ANALYZED"
    await db_session.commit()
    await db_session.refresh(prospect)

    detail_dto = ProspectDetailSchema.model_validate(prospect)

    assert detail_dto.lead_score == 85
    assert detail_dto.status == "ANALYZED"
    assert detail_dto.score_breakdown is not None
    assert detail_dto.score_breakdown["smb_focus"] == 35
    assert detail_dto.score_breakdown["saas_model"] == 25
    assert detail_dto.web_sources == []
    assert detail_dto.evidence_items == []


@pytest.mark.asyncio
async def test_isolation_from_real_database(db_session: AsyncSession) -> None:
    """Verify test runs in an isolated in-memory engine without polluting disk DB."""
    # Ensure URL is in-memory
    bind = db_session.bind
    assert bind is not None
    assert bind.url.database == ":memory:"

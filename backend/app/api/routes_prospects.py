"""API router for Prospect research, scoring, and grounded outreach drafts."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IcpProfile, Prospect
from app.db.seed_data import seed_initial_data
from app.db.session import get_db
from app.schemas.outreach_schema import (
    DraftOptionsSchema,
    OutreachDraftSchema,
)
from app.schemas.prospect_schema import (
    ProspectCreateSchema,
    ProspectDetailSchema,
    ProspectSummarySchema,
    extract_and_normalize_domain,
)
from app.services.outreach_service import generate_outreach_draft
from app.services.research_service import execute_prospect_research

router = APIRouter(prefix="/prospects", tags=["Prospects"])


@router.get("", response_model=list[ProspectSummarySchema])
async def list_prospects(
    db: Annotated[AsyncSession, Depends(get_db)],
    min_score: Annotated[
        int | None,
        Query(ge=0, le=100, description="Filter by minimum lead score"),
    ] = None,
    status_filter: Annotated[
        str | None,
        Query(alias="status", description="Filter by status (PENDING, ANALYZED)"),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search company name or domain"),
    ] = None,
) -> list[ProspectSummarySchema]:
    """Retrieve all prospect records with optional score, status, and search filters."""
    query = select(Prospect).order_by(Prospect.lead_score.desc(), Prospect.id.asc())

    if min_score is not None:
        query = query.where(Prospect.lead_score >= min_score)
    if status_filter is not None:
        query = query.where(Prospect.status == status_filter.upper())
    if search:
        pattern = f"%{search.lower()}%"
        query = query.where(
            Prospect.company_name.ilike(pattern) | Prospect.domain.ilike(pattern)
        )

    result = await db.execute(query)
    prospects = result.scalars().all()

    return [ProspectSummarySchema.model_validate(p) for p in prospects]


@router.post(
    "",
    response_model=ProspectSummarySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_prospect(
    payload: ProspectCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProspectSummarySchema:
    """Create a new custom prospect company for research and evaluation."""
    try:
        domain = extract_and_normalize_domain(payload.website_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # Reject duplicate domains
    query = select(Prospect).where(Prospect.domain == domain)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A prospect with domain '{domain}' already exists.",
        )

    # Bind to active ICP profile if one exists
    icp_query = select(IcpProfile.id).order_by(IcpProfile.id.asc()).limit(1)
    icp_result = await db.execute(icp_query)
    icp_id = icp_result.scalar_one_or_none() or 1

    new_prospect = Prospect(
        company_name=payload.company_name.strip(),
        website_url=payload.website_url.strip(),
        domain=domain,
        icp_id=icp_id,
        status="PENDING",
        lead_score=0,
    )
    db.add(new_prospect)
    await db.commit()
    await db.refresh(new_prospect)

    return ProspectSummarySchema.model_validate(new_prospect)


@router.post("/seed", response_model=list[ProspectSummarySchema])
async def trigger_seed(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProspectSummarySchema]:
    """Idempotently seed the default ICP and 10 Indian SMB SaaS companies."""
    _, prospects = await seed_initial_data(db)
    return [ProspectSummarySchema.model_validate(p) for p in prospects]


@router.get("/{prospect_id}", response_model=ProspectDetailSchema)
async def get_prospect_detail(
    prospect_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProspectDetailSchema:
    """Retrieve full detail for a prospect including web sources and evidence citations."""
    query = select(Prospect).where(Prospect.id == prospect_id)
    result = await db.execute(query)
    prospect = result.scalar_one_or_none()

    if prospect is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect {prospect_id} not found",
        )

    return ProspectDetailSchema.model_validate(prospect)


@router.post("/{prospect_id}/research", response_model=ProspectDetailSchema)
async def trigger_prospect_research(
    prospect_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProspectDetailSchema:
    """Trigger web crawling, grounding verification, and 100-point rubric calculation."""
    prospect = await execute_prospect_research(prospect_id, db)

    if prospect is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect {prospect_id} not found",
        )

    if prospect.status == "FAILED":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"Web crawling and evidence extraction failed for "
                f"{prospect.company_name} ({prospect.domain})."
            ),
        )

    return ProspectDetailSchema.model_validate(prospect)


@router.post("/{prospect_id}/draft", response_model=OutreachDraftSchema)
async def create_outreach_draft(
    prospect_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    options: DraftOptionsSchema | None = None,
) -> OutreachDraftSchema:
    """Generate an evidence-grounded cold outreach email draft citing verified facts."""
    opts = options or DraftOptionsSchema()
    draft = await generate_outreach_draft(
        prospect_id=prospect_id,
        session=db,
        template_type=opts.template_type,
        tone=opts.tone,
    )

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect {prospect_id} not found",
        )

    return OutreachDraftSchema.model_validate(draft)

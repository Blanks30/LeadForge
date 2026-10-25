"""API router for Ideal Customer Profile (ICP) management."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IcpProfile
from app.db.seed_data import DEFAULT_ICP
from app.db.session import get_db
from app.schemas.icp_schema import IcpResponse, IcpUpdateSchema

router = APIRouter()


@router.get("/icp", response_model=IcpResponse)
async def get_active_icp(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IcpResponse:
    """Retrieve the current active ICP criteria.

    If no ICP profile exists yet, creates and returns the default configuration.
    """
    query = select(IcpProfile).order_by(IcpProfile.id).limit(1)
    result = await db.execute(query)
    icp = result.scalar_one_or_none()

    if icp is None:
        icp = IcpProfile(**DEFAULT_ICP)
        db.add(icp)
        await db.commit()
        await db.refresh(icp)

    return IcpResponse.model_validate(icp)


@router.post("/icp", response_model=IcpResponse)
async def update_active_icp(
    payload: IcpUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IcpResponse:
    """Update active ICP criteria.

    Updates vertical, target geography, SMB criteria list, or tech keywords.
    """
    query = select(IcpProfile).order_by(IcpProfile.id).limit(1)
    result = await db.execute(query)
    icp = result.scalar_one_or_none()

    if icp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active ICP profile not found",
        )

    if payload.vertical is not None:
        icp.vertical = payload.vertical
    if payload.target_geo is not None:
        icp.target_geo = payload.target_geo
    if payload.smb_criteria is not None:
        icp.smb_criteria_json = json.dumps(payload.smb_criteria)
    if payload.tech_keywords is not None:
        icp.tech_keywords_json = json.dumps(payload.tech_keywords)

    await db.commit()
    await db.refresh(icp)

    return IcpResponse.model_validate(icp)

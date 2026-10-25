"""Pydantic schemas for Ideal Customer Profile (ICP) data."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IcpBase(BaseModel):
    """Shared ICP attributes."""

    vertical: str = Field(
        default="B2B SaaS serving SMBs / MSMEs",
        description="Target SaaS vertical",
    )
    target_geo: str = Field(
        default="India",
        description="Target geographic focus",
    )
    smb_criteria: list[str] = Field(
        default_factory=lambda: [
            "Self-serve onboarding",
            "Pricing in INR",
            "Mobile-first / WhatsApp capability",
            "Simplified SME workflows",
        ],
        description="List of SMB-focused criteria for evaluation",
    )
    tech_keywords: list[str] = Field(
        default_factory=lambda: [
            "SaaS",
            "cloud",
            "subscription",
            "API",
            "merchant",
            "invoicing",
            "kirana",
            "MSME",
        ],
        description="Keywords used to identify tech fit",
    )


class IcpUpdateSchema(BaseModel):
    """Schema for updating active ICP criteria."""

    vertical: str | None = None
    target_geo: str | None = None
    smb_criteria: list[str] | None = None
    tech_keywords: list[str] | None = None


class IcpResponse(IcpBase):
    """Full ICP profile representation returned by API."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def parse_from_orm(cls, data: Any) -> Any:
        """Parse JSON-serialized string columns from SQLAlchemy model instances."""
        if not isinstance(data, dict):
            raw_criteria = getattr(data, "smb_criteria_json", "[]")
            raw_keywords = getattr(data, "tech_keywords_json", "[]")

            if isinstance(raw_criteria, str):
                try:
                    criteria = json.loads(raw_criteria)
                except (json.JSONDecodeError, TypeError):
                    criteria = []
            else:
                criteria = raw_criteria or []

            if isinstance(raw_keywords, str):
                try:
                    keywords = json.loads(raw_keywords)
                except (json.JSONDecodeError, TypeError):
                    keywords = []
            else:
                keywords = raw_keywords or []

            return {
                "id": getattr(data, "id", None),
                "vertical": getattr(data, "vertical", "B2B SaaS serving SMBs / MSMEs"),
                "target_geo": getattr(data, "target_geo", "India"),
                "smb_criteria": criteria,
                "tech_keywords": keywords,
                "created_at": getattr(data, "created_at", None),
                "updated_at": getattr(data, "updated_at", None),
            }
        return data

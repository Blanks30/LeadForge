"""Pydantic schemas for Prospects, Web Sources, and Evidence Items."""

import json
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DOMAIN_REGEX = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def extract_and_normalize_domain(website_url: str) -> str:
    """Extract and normalize root domain from a validated website URL."""
    parsed = urlparse(website_url.strip())
    host = parsed.hostname or parsed.netloc
    if not host:
        raise ValueError("Cannot derive domain from URL.")

    if ":" in host:
        host = host.split(":")[0]

    domain = host.lower().strip().removeprefix("www.")

    if not DOMAIN_REGEX.match(domain):
        raise ValueError(f"Derived domain '{domain}' is not a valid domain name.")

    return domain


class ProspectCreateSchema(BaseModel):
    """Payload for creating a custom prospect company."""

    company_name: str = Field(
        min_length=1,
        max_length=255,
        description="Company name",
    )
    website_url: str = Field(
        min_length=1,
        max_length=1024,
        description="Website URL with http:// or https:// protocol",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional company description or operational notes",
    )

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        """Ensure company name is non-empty after stripping whitespace."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Company name cannot be blank.")
        return cleaned

    @field_validator("website_url")
    @classmethod
    def validate_website_url(cls, v: str) -> str:
        """Validate URL scheme and hostname structure."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Website URL cannot be blank.")

        parsed = urlparse(cleaned)
        if not parsed.scheme or parsed.scheme.lower() not in ("http", "https"):
            raise ValueError("Website URL must begin with http:// or https://")

        hostname = parsed.hostname or parsed.netloc
        if not hostname:
            raise ValueError("Website URL must include a valid hostname or domain.")

        return cleaned


class WebSourceSchema(BaseModel):
    """Scraped web source representation."""

    id: int
    prospect_id: int
    url: str
    page_type: str
    raw_text_snippet: str
    content_hash: str
    http_status: int
    publication_date: datetime | None = None
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceItemSchema(BaseModel):
    """Extracted evidence item with epistemic status and citation details."""

    id: int
    prospect_id: int
    source_id: int | None = None
    category: str
    rubric_criterion: str | None = None
    claim_text: str
    exact_quote: str | None = None
    epistemic_status: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    gemini_reasoning: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProspectBase(BaseModel):
    """Base fields for SaaS prospect companies."""

    company_name: str = Field(min_length=1, description="Company name")
    website_url: str = Field(min_length=1, description="Website URL")
    domain: str = Field(
        pattern=r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Normalized root domain",
    )
    hq_location: str | None = None
    employee_range: str | None = None


class ProspectSummarySchema(ProspectBase):
    """Lightweight prospect summary for dashboard table and lists."""

    id: int
    icp_id: int
    lead_score: int = Field(ge=0, le=100, default=0)
    score_breakdown: dict[str, int] | None = None
    status: str = Field(default="PENDING")
    researched_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def parse_score_breakdown(cls, data: Any) -> Any:
        """Parse JSON score_breakdown string into a typed dictionary if present."""
        if not isinstance(data, dict):
            raw_breakdown = getattr(data, "score_breakdown_json", None)
            parsed_breakdown = None
            if isinstance(raw_breakdown, str):
                try:
                    parsed_breakdown = json.loads(raw_breakdown)
                except (json.JSONDecodeError, TypeError):
                    parsed_breakdown = None

            return {
                "id": getattr(data, "id", None),
                "icp_id": getattr(data, "icp_id", None),
                "company_name": getattr(data, "company_name", ""),
                "website_url": getattr(data, "website_url", ""),
                "domain": getattr(data, "domain", ""),
                "hq_location": getattr(data, "hq_location", None),
                "employee_range": getattr(data, "employee_range", None),
                "lead_score": getattr(data, "lead_score", 0),
                "status": getattr(data, "status", "PENDING"),
                "researched_at": getattr(data, "researched_at", None),
                "created_at": getattr(data, "created_at", None),
                "updated_at": getattr(data, "updated_at", None),
                "score_breakdown_json": raw_breakdown,
                "score_breakdown": parsed_breakdown,
                "web_sources": getattr(data, "web_sources", []),
                "evidence_items": getattr(data, "evidence_items", []),
            }
        elif "score_breakdown" not in data and "score_breakdown_json" in data:
            raw = data.get("score_breakdown_json")
            if isinstance(raw, str):
                try:
                    data["score_breakdown"] = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    data["score_breakdown"] = None
        return data


class ProspectDetailSchema(ProspectSummarySchema):
    """Detailed prospect view including score breakdown, sources, and evidence."""

    score_breakdown_json: str | None = None
    web_sources: list[WebSourceSchema] = []
    evidence_items: list[EvidenceItemSchema] = []
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

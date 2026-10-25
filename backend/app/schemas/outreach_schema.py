"""Pydantic schemas for generated outreach email drafts."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DraftOptionsSchema(BaseModel):
    """Options for generating an evidence-grounded outreach email draft."""

    template_type: str = Field(
        default="EVIDENCE_PROBLEM_SOLUTION",
        description="Template style (e.g. EVIDENCE_PROBLEM_SOLUTION)",
    )
    tone: str = Field(
        default="CONSULTATIVE_DIRECT",
        description="Tone of the email (e.g. CONSULTATIVE_DIRECT)",
    )


class OutreachDraftSchema(BaseModel):
    """Serialized representation of an evidence-backed cold email draft."""

    id: int
    prospect_id: int
    template_type: str
    subject_line: str
    body_text: str
    citations_json: str
    citations: list[int] = []
    tone: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def parse_citations(cls, data: Any) -> Any:
        """Parse citations_json into a list of integer IDs if needed."""
        if not isinstance(data, dict):
            raw_citations = getattr(data, "citations_json", "[]")
            parsed_citations: list[int] = []
            if isinstance(raw_citations, str):
                try:
                    loaded = json.loads(raw_citations)
                    if isinstance(loaded, list):
                        parsed_citations = [int(x) for x in loaded if str(x).isdigit()]
                except (json.JSONDecodeError, TypeError, ValueError):
                    parsed_citations = []

            return {
                "id": getattr(data, "id", None),
                "prospect_id": getattr(data, "prospect_id", None),
                "template_type": getattr(
                    data, "template_type", "EVIDENCE_PROBLEM_SOLUTION"
                ),
                "subject_line": getattr(data, "subject_line", ""),
                "body_text": getattr(data, "body_text", ""),
                "citations_json": raw_citations,
                "citations": parsed_citations,
                "tone": getattr(data, "tone", "CONSULTATIVE_DIRECT"),
                "created_at": getattr(data, "created_at", None),
                "updated_at": getattr(data, "updated_at", None),
            }
        return data

"""Evidence-grounded outreach draft generation service.

Generates concise, consultative cold email drafts (under 120 words) following
AGENTS.md §4.2: calls Gemini with approved FACT evidence and the structured
OutreachDraftResponse schema when a live API key is configured; falls back to
a deterministic template generator when in mock mode or when Gemini is unavailable.

Enforces zero-send safety: no email dispatch APIs exist in this codebase.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import OutreachDraft, Prospect
from app.services.gemini_client import (
    GeminiConfigError,
    GeminiError,
    get_gemini_client,
)

logger = logging.getLogger("leadforge.outreach")


def _build_template_draft(
    prospect: Prospect,
    verified_facts: list[Any],
) -> tuple[str, str, list[int]]:
    """Deterministic fallback template for mock mode or when Gemini is unavailable.

    Returns (subject_line, body_text, cited_evidence_ids).
    Only references verified FACT items to maintain epistemic safety.
    """
    if not verified_facts:
        subject = f"Connecting with {prospect.company_name} on SMB SaaS growth"
        body = (
            f"Hi {prospect.company_name} team,\n\n"
            f"I came across {prospect.domain} while researching B2B SaaS platforms serving "
            "SMBs in India. Would love to connect briefly to share insights from our work "
            "with similar growth founders.\n\n"
            "Best regards,\nAarav Mehta | LeadForge"
        )
        return subject, body, []

    fact1 = verified_facts[0]
    fact2 = verified_facts[1] if len(verified_facts) > 1 else None

    subject = f"Scaling {prospect.company_name}'s {fact1.category.lower().replace('_', ' ')} strategy"

    body_lines = [
        f"Hi {prospect.company_name} team,",
        "",
        f"I noticed that {fact1.claim_text} [Ref: #{fact1.id}].",
    ]
    cited_ids = [fact1.id]

    if fact2:
        body_lines.append(
            f"Additionally, observed that {fact2.claim_text} [Ref: #{fact2.id}]."
        )
        cited_ids.append(fact2.id)

    body_lines.extend(
        [
            "",
            "We help Indian B2B SaaS teams streamline high-conversion prospect outreach without generic fluff.",
            "Would you be open to a 10-minute discussion this Thursday?",
            "",
            "Best regards,",
            "Aarav Mehta | LeadForge",
        ]
    )
    return subject, "\n".join(body_lines), cited_ids


async def generate_outreach_draft(
    prospect_id: int,
    session: AsyncSession,
    template_type: str = "EVIDENCE_PROBLEM_SOLUTION",
    tone: str = "CONSULTATIVE_DIRECT",
) -> OutreachDraft | None:
    """Generate and persist an evidence-grounded email draft for the prospect.

    Strategy (in priority order):
    1. Live Gemini: If GEMINI_API_KEY is set and USE_MOCK_APIS is False, call
       Gemini with the AGENTS.md §4.2 prompt and structured OutreachDraftResponse schema.
    2. Template fallback: Used when in mock mode or on any transient Gemini error.

    Strict grounding rule: Only FACT evidence items are passed to Gemini or referenced
    by the template. INFERENCE and UNKNOWN items are excluded from outreach citations.
    """
    query = select(Prospect).where(Prospect.id == prospect_id)
    result = await session.execute(query)
    prospect = result.scalar_one_or_none()

    if prospect is None:
        return None

    # Filter only verified FACT items for citation
    verified_facts = [
        item for item in prospect.evidence_items if item.epistemic_status == "FACT"
    ]

    subject: str
    body: str
    cited_ids: list[int]
    generation_mode: str

    # Determine whether to attempt live Gemini outreach generation
    use_live_gemini = (
        not settings.USE_MOCK_APIS
        and bool(settings.GEMINI_API_KEY)
        and bool(verified_facts)
    )

    if use_live_gemini:
        approved_evidence: list[dict[str, Any]] = [
            {
                "id": item.id,
                "category": item.category,
                "rubric_criterion": item.rubric_criterion,
                "claim_text": item.claim_text,
                "exact_quote": item.exact_quote,
                "epistemic_status": item.epistemic_status,
                "confidence_score": item.confidence_score,
            }
            for item in verified_facts
        ]

        try:
            gemini_client = get_gemini_client()
            draft_response = await gemini_client.generate_outreach_draft(
                company_name=prospect.company_name,
                approved_evidence=approved_evidence,
                tone=tone,
            )
            subject = draft_response.subject_line
            body = draft_response.body_text
            # Use IDs Gemini actually cited; fall back to all approved IDs if none returned
            cited_ids = (
                draft_response.referenced_evidence_ids
                if draft_response.referenced_evidence_ids
                else [item["id"] for item in approved_evidence]
            )
            generation_mode = "GEMINI_LIVE"
            logger.info(
                "Gemini outreach draft generated for '%s' (%d words, %d citations).",
                prospect.company_name,
                draft_response.word_count,
                len(cited_ids),
            )
        except GeminiConfigError:
            # Configuration error: unexpected since we checked the key above; fall through
            logger.warning(
                "Gemini config error generating outreach for '%s'; using template fallback.",
                prospect.company_name,
            )
            subject, body, cited_ids = _build_template_draft(prospect, verified_facts)
            generation_mode = "TEMPLATE_FALLBACK"
        except GeminiError as exc:
            # Transient Gemini errors (rate limit, network, unavailable): graceful fallback
            logger.warning(
                "Gemini outreach generation failed for '%s' (%s); using template fallback.",
                prospect.company_name,
                type(exc).__name__,
            )
            subject, body, cited_ids = _build_template_draft(prospect, verified_facts)
            generation_mode = "TEMPLATE_FALLBACK"
    else:
        subject, body, cited_ids = _build_template_draft(prospect, verified_facts)
        generation_mode = (
            "TEMPLATE_MOCK" if settings.USE_MOCK_APIS else "TEMPLATE_NO_KEY"
        )
        if not verified_facts:
            generation_mode = "TEMPLATE_NO_FACTS"

    logger.debug(
        "Outreach draft mode=%s for prospect=%d (%s)",
        generation_mode,
        prospect_id,
        prospect.company_name,
    )

    # Determine human-friendly generation source label
    # "GEMINI_AI" vs "DETERMINISTIC_TEMPLATE"
    source_label = (
        "GEMINI_AI" if generation_mode == "GEMINI_LIVE" else "DETERMINISTIC_TEMPLATE"
    )

    draft = OutreachDraft(
        prospect_id=prospect.id,
        template_type=template_type,
        subject_line=subject,
        body_text=body,
        citations_json=json.dumps(cited_ids),
        tone=tone,
        generation_source=source_label,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    return draft

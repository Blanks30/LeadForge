"""Research orchestration and evidence verification service.

Executes web research (via mock adapter or live crawler), verifies grounding
using exact substring matching, and computes explainable rubric scores.
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import EvidenceItem, Prospect, WebSource
from app.services.gemini_client import (
    GeminiAuthError,
    GeminiConfigError,
    GeminiError,
    get_gemini_client,
)
from app.services.scoring_engine import calculate_lead_score
from app.services.tinyfish_client import get_tinyfish_client

logger = logging.getLogger("leadforge.research")


def verify_grounding(quote: str | None, raw_scraped_text: str | None) -> bool:
    """Validate that an extracted quote exists verbatim in source text.

    Normalizes whitespace and case to ensure robust verification.
    """
    if not quote or not raw_scraped_text:
        return False
    normalized_quote = " ".join(quote.lower().split())
    normalized_source = " ".join(raw_scraped_text.lower().split())
    return normalized_quote in normalized_source


async def execute_prospect_research(
    prospect_id: int,
    session: AsyncSession,
) -> Prospect | None:
    """Execute research, extract grounded evidence, and score the prospect.

    Utilizes TinyFish client adapter (live HTTP or deterministic mock fallback)
    for target Indian SMB SaaS companies. Cleans prior run artifacts before repopulating.
    """
    query = select(Prospect).where(Prospect.id == prospect_id)
    result = await session.execute(query)
    prospect = result.scalar_one_or_none()

    if prospect is None:
        return None

    # Retrieve payload from client adapter (mock or live)
    crawler = get_tinyfish_client()
    try:
        payload = await crawler.crawl_prospect(prospect.domain, prospect.website_url)
    except (httpx.HTTPError, OSError, TimeoutError, ValueError) as exc:
        logger.warning(
            "Crawl failed for '%s' (%s): %s",
            prospect.domain,
            type(exc).__name__,
            exc,
        )
        payload = None

    if not payload:
        prospect.status = "FAILED"
        await session.commit()
        await session.refresh(prospect)
        return prospect

    try:
        # Clear previous web sources and evidence if re-running research
        prospect.web_sources.clear()
        prospect.evidence_items.clear()
        await session.flush()

        # 1. Store WebSources
        created_sources: list[WebSource] = []
        for s_data in payload.get("sources", []):
            snippet = s_data["raw_text_snippet"]
            content_hash = hashlib.sha256(snippet.encode("utf-8")).hexdigest()
            source = WebSource(
                prospect_id=prospect.id,
                url=s_data["url"],
                page_type=s_data.get("page_type", "HOMEPAGE"),
                raw_text_snippet=snippet,
                content_hash=content_hash,
                http_status=200,
                fetched_at=datetime.now(UTC),
            )
            session.add(source)
            created_sources.append(source)

        await session.flush()

        # 2. Extract evidence: live Gemini extraction if live mode is enabled, else mock payload
        is_live_mode = not settings.USE_MOCK_APIS and bool(settings.GEMINI_API_KEY)

        gemini_hq_location: str | None = None
        gemini_employee_range: str | None = None
        raw_evidence_items: list[dict[str, Any]] = []

        if is_live_mode and created_sources:
            gemini_client = get_gemini_client()
            sources_input = [
                {
                    "url": s.url,
                    "page_type": s.page_type,
                    "raw_text_snippet": s.raw_text_snippet,
                }
                for s in created_sources
            ]
            try:
                extraction = await gemini_client.extract_evidence(
                    company_name=prospect.company_name,
                    sources=sources_input,
                )
            except (GeminiConfigError, GeminiAuthError) as exc:
                # Fatal configuration / credential errors: surface immediately
                logger.error(
                    "Gemini extraction aborted for '%s': %s",
                    prospect.company_name,
                    type(exc).__name__,
                )
                raise
            except GeminiError as exc:
                # Transient Gemini errors (rate limit, network, unavailable):
                # log and fall back to mock payload evidence so the run completes
                logger.warning(
                    "Gemini extraction failed for '%s' (%s); falling back to mock evidence.",
                    prospect.company_name,
                    type(exc).__name__,
                )
                extraction = None

            if extraction is not None:
                for item in extraction.evidence_items:
                    matched_idx = 0
                    for s_i, s in enumerate(created_sources):
                        if item.source_url and s.url.rstrip(
                            "/"
                        ) == item.source_url.rstrip("/"):
                            matched_idx = s_i
                            break
                    raw_evidence_items.append(
                        {
                            "category": item.category,
                            "rubric_criterion": item.rubric_criterion,
                            "claim_text": item.claim_text,
                            "exact_quote": item.exact_quote,
                            "epistemic_status": item.epistemic_status,
                            "confidence_score": item.confidence_score,
                            "gemini_reasoning": item.gemini_reasoning,
                            "source_index": matched_idx,
                        }
                    )
                gemini_hq_location = extraction.hq_location
                gemini_employee_range = extraction.employee_range
            else:
                # Transient fallback: use evidence carried in the crawl payload
                raw_evidence_items = payload.get("evidence_items", [])
        else:
            raw_evidence_items = payload.get("evidence_items", [])

        # 3. Ground and persist Evidence Items
        created_evidence: list[EvidenceItem] = []
        for e_data in raw_evidence_items:
            s_idx = e_data.get("source_index", 0)
            matched_source = (
                created_sources[s_idx] if s_idx < len(created_sources) else None
            )
            source_id = matched_source.id if matched_source else None

            quote = e_data.get("exact_quote")
            epistemic = e_data.get("epistemic_status", "UNKNOWN")
            reasoning = e_data.get("gemini_reasoning")

            # Grounding check: verify that FACT quotes appear verbatim in source snippet
            if epistemic == "FACT":
                source_text = matched_source.raw_text_snippet if matched_source else ""
                is_grounded = verify_grounding(quote, source_text)
                if not is_grounded:
                    # Anti-hallucination defense: degrade ungrounded claim to inference
                    epistemic = "INFERENCE"
                    reasoning = (
                        reasoning + " | " if reasoning else ""
                    ) + "Ungrounded quote degraded to inference."
            elif epistemic == "UNKNOWN":
                quote = None

            evidence = EvidenceItem(
                prospect_id=prospect.id,
                source_id=source_id,
                category=e_data["category"],
                rubric_criterion=e_data.get("rubric_criterion"),
                claim_text=e_data["claim_text"],
                exact_quote=quote,
                epistemic_status=epistemic,
                confidence_score=e_data.get("confidence_score", 1.0),
                gemini_reasoning=reasoning,
                created_at=datetime.now(UTC),
            )
            session.add(evidence)
            created_evidence.append(evidence)

        await session.flush()

        # 3. Calculate deterministic lead score
        total_score, breakdown = calculate_lead_score(created_evidence)

        # 4. Update prospect attributes
        # Apply payload-level defaults first, then override with Gemini-enriched values
        # (Gemini enrichment takes precedence when available)
        prospect.hq_location = payload.get("hq_location", prospect.hq_location)
        prospect.employee_range = payload.get("employee_range", prospect.employee_range)
        if gemini_hq_location:
            prospect.hq_location = gemini_hq_location
        if gemini_employee_range:
            prospect.employee_range = gemini_employee_range
        prospect.lead_score = total_score
        prospect.score_breakdown_json = json.dumps(breakdown)
        prospect.status = "ANALYZED"
        prospect.researched_at = datetime.now(UTC)

        await session.commit()
        await session.refresh(prospect)

        return prospect
    except (ValueError, KeyError, AttributeError, OSError, RuntimeError) as exc:
        logger.error(
            "Research pipeline failed for prospect_id=%d (%s): %s",
            prospect_id,
            type(exc).__name__,
            exc,
        )
        await session.rollback()
        prospect.status = "FAILED"
        await session.commit()
        await session.refresh(prospect)
        return prospect

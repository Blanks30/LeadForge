"""Research orchestration and evidence verification service.

Executes web research (via mock adapter or live crawler), verifies grounding
using exact substring matching, and computes explainable rubric scores.
"""

import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EvidenceItem, Prospect, WebSource
from app.services.scoring_engine import calculate_lead_score
from app.services.tinyfish_client import get_tinyfish_client


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
    payload = await crawler.crawl_prospect(prospect.domain, prospect.website_url)
    if not payload:
        return None

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

    # 2. Extract and Ground Evidence Items
    created_evidence: list[EvidenceItem] = []
    for e_data in payload.get("evidence_items", []):
        s_idx = e_data.get("source_index", 0)
        matched_source = (
            created_sources[s_idx] if s_idx < len(created_sources) else None
        )
        source_id = matched_source.id if matched_source else None

        quote = e_data.get("exact_quote")
        epistemic = e_data.get("epistemic_status", "UNKNOWN")

        # Grounding check: verify that FACT quotes appear verbatim in source snippet
        if epistemic == "FACT":
            source_text = matched_source.raw_text_snippet if matched_source else ""
            is_grounded = verify_grounding(quote, source_text)
            if not is_grounded:
                # Anti-hallucination defense: degrade ungrounded claim
                epistemic = "INFERENCE"
                e_data["gemini_reasoning"] = "Ungrounded quote degraded to inference."

        evidence = EvidenceItem(
            prospect_id=prospect.id,
            source_id=source_id,
            category=e_data["category"],
            rubric_criterion=e_data.get("rubric_criterion"),
            claim_text=e_data["claim_text"],
            exact_quote=quote,
            epistemic_status=epistemic,
            confidence_score=e_data.get("confidence_score", 1.0),
            gemini_reasoning=e_data.get("gemini_reasoning"),
            created_at=datetime.now(UTC),
        )
        session.add(evidence)
        created_evidence.append(evidence)

    await session.flush()

    # 3. Calculate deterministic lead score
    total_score, breakdown = calculate_lead_score(created_evidence)

    # 4. Update prospect attributes
    prospect.hq_location = payload.get("hq_location", prospect.hq_location)
    prospect.employee_range = payload.get("employee_range", prospect.employee_range)
    prospect.lead_score = total_score
    prospect.score_breakdown_json = json.dumps(breakdown)
    prospect.status = "ANALYZED"
    prospect.researched_at = datetime.now(UTC)

    await session.commit()
    await session.refresh(prospect)

    return prospect

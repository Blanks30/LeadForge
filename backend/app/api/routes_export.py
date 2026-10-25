"""API router for CSV prospect export with formula injection defense (CWE-1236)."""

import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Prospect
from app.db.session import get_db

router = APIRouter(prefix="/export", tags=["Export"])


def sanitize_csv_cell(value: str | None) -> str:
    """Sanitize cell against CSV Formula Injection (CWE-1236).

    Prefixes characters that Excel or Google Sheets would interpret as formulas.
    """
    if not value:
        return ""
    str_val = str(value)
    if str_val.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{str_val}"
    return str_val


@router.get("/csv")
async def export_prospects_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Export all researched and pending prospects to a clean, sanitized CSV."""
    query = select(Prospect).order_by(Prospect.lead_score.desc(), Prospect.id.asc())
    result = await db.execute(query)
    prospects = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")

    # Header Row
    writer.writerow(
        [
            "Company Name",
            "Website Domain",
            "Lead Score",
            "Status",
            "Key Fact 1",
            "Key Fact 2",
            "Evidence Source URLs",
            "Outreach Subject Line",
            "Outreach Body",
        ]
    )

    for p in prospects:
        fact1 = ""
        fact2 = ""
        facts = [item for item in p.evidence_items if item.epistemic_status == "FACT"]
        if len(facts) >= 1:
            fact1 = f"{facts[0].claim_text} (Quote: '{facts[0].exact_quote}')"
        if len(facts) >= 2:
            fact2 = f"{facts[1].claim_text} (Quote: '{facts[1].exact_quote}')"

        source_urls = "; ".join({s.url for s in p.web_sources})

        subject = ""
        body = ""
        if p.outreach_drafts:
            latest_draft = p.outreach_drafts[-1]
            subject = latest_draft.subject_line
            body = latest_draft.body_text

        writer.writerow(
            [
                sanitize_csv_cell(p.company_name),
                sanitize_csv_cell(p.domain),
                sanitize_csv_cell(str(p.lead_score)),
                sanitize_csv_cell(p.status),
                sanitize_csv_cell(fact1),
                sanitize_csv_cell(fact2),
                sanitize_csv_cell(source_urls),
                sanitize_csv_cell(subject),
                sanitize_csv_cell(body),
            ]
        )

    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=leadforge_prospects.csv"},
    )

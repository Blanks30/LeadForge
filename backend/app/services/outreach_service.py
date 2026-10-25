"""Evidence-grounded outreach draft generation service.

Generates concise, consultative cold email drafts (under 120 words) citing
only verified evidence item IDs (e.g., '[Ref: #1]'). Enforces zero-send safety.
"""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OutreachDraft, Prospect


async def generate_outreach_draft(
    prospect_id: int,
    session: AsyncSession,
    template_type: str = "EVIDENCE_PROBLEM_SOLUTION",
    tone: str = "CONSULTATIVE_DIRECT",
) -> OutreachDraft | None:
    """Generate and store an evidence-grounded email draft.

    Strict grounding rule: Only references claims present in verified FACT evidence items.
    """
    query = select(Prospect).where(Prospect.id == prospect_id)
    result = await session.execute(query)
    prospect = result.scalar_one_or_none()

    if prospect is None:
        return None

    # Filter for verified facts
    verified_facts = [
        item for item in prospect.evidence_items if item.epistemic_status == "FACT"
    ]

    if not verified_facts:
        subject = f"Connecting with {prospect.company_name} on SMB SaaS growth"
        body = (
            f"Hi {prospect.company_name} team,\n\n"
            f"I came across {prospect.domain} while researching B2B SaaS platforms serving SMBs in India. "
            "Would love to connect briefly to share insights from our work with similar growth founders.\n\n"
            "Best regards,\nAarav Mehta | LeadForge"
        )
        cited_ids: list[int] = []
    else:
        # Construct grounded subject and body referencing verified facts
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
        body = "\n".join(body_lines)

    draft = OutreachDraft(
        prospect_id=prospect.id,
        template_type=template_type,
        subject_line=subject,
        body_text=body,
        citations_json=json.dumps(cited_ids),
        tone=tone,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    return draft

"""Idempotent seed data for LeadForge initial evaluation.

Creates the default ICP profile and seeds the 10 target Indian SMB SaaS
companies specified in DATABASE.md.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IcpProfile, Prospect
from app.db.session import async_session_maker

SAMPLE_COMPANIES: list[dict[str, str]] = [
    {
        "company_name": "Khatabook",
        "website_url": "https://khatabook.com",
        "domain": "khatabook.com",
    },
    {
        "company_name": "myBillBook (FloBiz)",
        "website_url": "https://mybillbook.in",
        "domain": "mybillbook.in",
    },
    {
        "company_name": "Dukaan",
        "website_url": "https://mydukaan.io",
        "domain": "mydukaan.io",
    },
    {
        "company_name": "Vyapar",
        "website_url": "https://vyaparapp.in",
        "domain": "vyaparapp.in",
    },
    {
        "company_name": "Shiprocket",
        "website_url": "https://shiprocket.in",
        "domain": "shiprocket.in",
    },
    {
        "company_name": "Classplus",
        "website_url": "https://classplus.co",
        "domain": "classplus.co",
    },
    {
        "company_name": "Restroworks (POSist)",
        "website_url": "https://restroworks.com",
        "domain": "restroworks.com",
    },
    {
        "company_name": "Exotel",
        "website_url": "https://exotel.com",
        "domain": "exotel.com",
    },
    {
        "company_name": "Zoho",
        "website_url": "https://zoho.com",
        "domain": "zoho.com",
    },
    {
        "company_name": "Freshworks",
        "website_url": "https://freshworks.com",
        "domain": "freshworks.com",
    },
]

DEFAULT_ICP: dict[str, str] = {
    "vertical": "B2B SaaS serving SMBs / MSMEs",
    "target_geo": "India",
    "smb_criteria_json": (
        '["Self-serve onboarding", "Pricing in INR", '
        '"Mobile-first / WhatsApp capability", "Simplified SME workflows"]'
    ),
    "tech_keywords_json": (
        '["SaaS", "cloud", "subscription", "API", '
        '"merchant", "invoicing", "kirana", "MSME"]'
    ),
}


async def _seed_with_session(
    session: AsyncSession,
) -> tuple[IcpProfile, list[Prospect]]:
    """Internal helper to seed ICP and 10 prospects within an active session."""
    # 1. Get or create active ICP
    icp_query = select(IcpProfile).order_by(IcpProfile.id).limit(1)
    icp_res = await session.execute(icp_query)
    icp = icp_res.scalar_one_or_none()

    if icp is None:
        icp = IcpProfile(**DEFAULT_ICP)
        session.add(icp)
        await session.flush()

    # 2. Query existing prospects by unique domain to guarantee idempotency
    domains = [c["domain"] for c in SAMPLE_COMPANIES]
    existing_res = await session.execute(
        select(Prospect).where(Prospect.domain.in_(domains))
    )
    existing_by_domain = {p.domain: p for p in existing_res.scalars().all()}

    seeded_prospects: list[Prospect] = []
    for company in SAMPLE_COMPANIES:
        domain = company["domain"]
        if domain in existing_by_domain:
            seeded_prospects.append(existing_by_domain[domain])
        else:
            # Seed unresearched prospect record without fabricated evidence
            new_prospect = Prospect(
                icp_id=icp.id,
                company_name=company["company_name"],
                website_url=company["website_url"],
                domain=domain,
                status="PENDING",
                lead_score=0,
                score_breakdown_json=None,
                researched_at=None,
                hq_location=None,
                employee_range=None,
            )
            session.add(new_prospect)
            seeded_prospects.append(new_prospect)

    await session.commit()

    # Refresh newly added objects to populate generated IDs and defaults
    for prospect in seeded_prospects:
        await session.refresh(prospect)
    await session.refresh(icp)

    return icp, seeded_prospects


async def seed_initial_data(
    session: AsyncSession | None = None,
) -> tuple[IcpProfile, list[Prospect]]:
    """Seed the default ICP profile and 10 sample Indian SaaS companies.

    Idempotent: Uses the unique domain constraint as a stable identifier.
    Does not duplicate records on subsequent calls. Makes zero network requests.
    """
    if session is not None:
        return await _seed_with_session(session)

    async with async_session_maker() as new_session:
        return await _seed_with_session(new_session)

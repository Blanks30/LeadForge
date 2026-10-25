"""Deterministic 100-point lead scoring engine.

Implements the mathematical rubric specified in AGENTS.md Section 3:
Total Lead Score (0–100) = SMB Focus (35) + SaaS Model (25) + Growth Signals (20) + Evidence Quality (20)
"""

from app.db.models import EvidenceItem


def calculate_lead_score(
    evidence_items: list[EvidenceItem],
) -> tuple[int, dict[str, int]]:
    """Compute transparent 100-point lead score based on verified evidence items.

    Returns:
        tuple[int, dict[str, int]]: (total_score clamped between 0 and 100, score_breakdown)
    """
    # Group rubric criteria present in verified facts or reasoned inferences
    active_criteria: set[str] = set()
    verified_fact_count = 0
    distinct_sources: set[int] = set()

    for item in evidence_items:
        if item.rubric_criterion and item.epistemic_status in ("FACT", "INFERENCE"):
            active_criteria.add(item.rubric_criterion)

        if item.epistemic_status == "FACT" and item.exact_quote:
            verified_fact_count += 1
            if item.source_id is not None:
                distinct_sources.add(item.source_id)

    # Dimension 1: SMB Focus in India (Max 35 pts)
    smb_points = 0
    if "MSME_EXPLICIT_FOCUS" in active_criteria:
        smb_points += 15
    if "INR_PRICING" in active_criteria:
        smb_points += 10
    if "MOBILE_WHATSAPP_ONBOARDING" in active_criteria:
        smb_points += 10
    smb_points = min(35, smb_points)

    # Dimension 2: SaaS Delivery Model (Max 25 pts)
    saas_points = 0
    if "CLOUD_SAAS_ARCHITECTURE" in active_criteria:
        saas_points += 15
    if "TRANSPARENT_TIER_PRICING" in active_criteria:
        saas_points += 10
    saas_points = min(25, saas_points)

    # Dimension 3: Growth & Market Signals (Max 20 pts)
    growth_points = 0
    if "RECENT_PRODUCT_UPDATE" in active_criteria:
        growth_points += 10
    if "HIRING_EXPANSION_SIGNAL" in active_criteria:
        growth_points += 10
    growth_points = min(20, growth_points)

    # Dimension 4: Evidence Quality (Max 20 pts)
    evidence_points = 0
    if verified_fact_count >= 3:
        evidence_points += 10
    elif verified_fact_count >= 1:
        evidence_points += 5

    if len(distinct_sources) >= 2:
        evidence_points += 10
    elif len(distinct_sources) >= 1:
        evidence_points += 5
    evidence_points = min(20, evidence_points)

    total_score = smb_points + saas_points + growth_points + evidence_points
    total_score = max(0, min(100, total_score))

    breakdown: dict[str, int] = {
        "smb_focus": smb_points,
        "saas_model": saas_points,
        "growth_signals": growth_points,
        "evidence_quality": evidence_points,
        "total": total_score,
    }

    return total_score, breakdown

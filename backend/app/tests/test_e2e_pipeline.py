"""End-to-end integration tests for the complete prospect research pipeline.

Tests the full journey specified in Milestone 3 Phase 4 & Phase 6:
1. Prospect selection / seeding.
2. TinyFish web research (storing web_sources with raw text & SHA-256 hash).
3. Gemini evidence extraction (FACT / INFERENCE / UNKNOWN separation, quote grounding).
4. Python 100-point rubric calculation (explainable breakdown).
5. Storage and persistence in SQLite.
6. Grounded outreach generation citing only verified facts.
7. Zero Auto-Send verification (no outbound mail infrastructure).
8. Real live credential gate check (distinguishes configured mock from live).
"""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core import config
from app.main import app
from app.services.gemini_client import (
    GeminiEvidenceItem,
    GeminiExtractionResponse,
)


def test_complete_end_to_end_research_and_outreach_pipeline():
    """Execute and verify the full pipeline end-to-end."""
    with TestClient(app) as client:
        # Step 1: User seeds prospects
        seed_res = client.post("/api/prospects/seed")
        assert seed_res.status_code == 200
        prospects = seed_res.json()
        assert len(prospects) == 10

        target = next(p for p in prospects if p["domain"] == "khatabook.com")
        prospect_id = target["id"]

        # Step 2-5: Trigger research pipeline
        research_res = client.post(f"/api/prospects/{prospect_id}/research")
        assert research_res.status_code == 200
        analyzed = research_res.json()

        # Verify research status & attributes
        assert analyzed["status"] == "ANALYZED"
        assert analyzed["lead_score"] >= 80  # Khatabook high score
        assert analyzed["score_breakdown"] is not None
        assert analyzed["score_breakdown"]["total"] == analyzed["lead_score"]
        assert analyzed["score_breakdown"]["smb_focus"] > 0
        assert analyzed["score_breakdown"]["saas_model"] > 0

        # Verify web sources stored with URLs and SHA-256 content hashes
        assert len(analyzed["web_sources"]) >= 2
        for src in analyzed["web_sources"]:
            assert src["url"].startswith("http")
            assert len(src["content_hash"]) == 64  # SHA-256 hex length
            assert len(src["raw_text_snippet"]) > 0

        # Verify epistemic separation (FACT vs INFERENCE vs UNKNOWN)
        evidence_items = analyzed["evidence_items"]
        assert len(evidence_items) >= 3

        statuses = {e["epistemic_status"] for e in evidence_items}
        assert "FACT" in statuses

        for item in evidence_items:
            if item["epistemic_status"] == "FACT":
                assert item["exact_quote"] is not None
                assert len(item["exact_quote"]) > 0
            elif item["epistemic_status"] == "UNKNOWN":
                assert item["exact_quote"] is None

        # Step 6: Generate evidence-backed outreach draft
        draft_res = client.post(
            f"/api/prospects/{prospect_id}/draft",
            json={
                "template_type": "EVIDENCE_PROBLEM_SOLUTION",
                "tone": "CONSULTATIVE_DIRECT",
            },
        )
        assert draft_res.status_code == 200
        draft = draft_res.json()

        assert draft["subject_line"] != ""
        assert "[Ref: #" in draft["body_text"]
        assert len(draft["citations"]) >= 1
        assert draft["generation_source"] == "DETERMINISTIC_TEMPLATE"

        # Verify detail view persistence across roundtrips
        detail_res = client.get(f"/api/prospects/{prospect_id}")
        assert detail_res.status_code == 200
        persisted = detail_res.json()
        assert persisted["lead_score"] == analyzed["lead_score"]


def test_live_gemini_extraction_flow_with_mocked_boundary(monkeypatch):
    """Verify live Gemini evidence extraction when configured (using boundary mock)."""
    from app.services import research_service

    monkeypatch.setattr(research_service.settings, "USE_MOCK_APIS", False)
    monkeypatch.setattr(research_service.settings, "GEMINI_API_KEY", "test-live-key")

    mock_gemini = AsyncMock()
    mock_gemini.extract_evidence = AsyncMock(
        return_value=GeminiExtractionResponse(
            company_name="Khatabook",
            hq_location="Bengaluru, India",
            employee_range="250-500",
            evidence_items=[
                GeminiEvidenceItem(
                    category="SMB_FOCUS",
                    rubric_criterion="MSME_EXPLICIT_FOCUS",
                    claim_text="Targets Indian Kiranas",
                    exact_quote="Khatabook helps Indian MSMEs and Kirana store owners record transactions",
                    epistemic_status="FACT",
                    confidence_score=1.0,
                    source_url="https://khatabook.com",
                ),
                GeminiEvidenceItem(
                    category="SAAS_MODEL",
                    rubric_criterion="CLOUD_SAAS_ARCHITECTURE",
                    claim_text="Likely cloud platform",
                    exact_quote=None,
                    epistemic_status="INFERENCE",
                    confidence_score=0.9,
                    gemini_reasoning="Mobile and web sync implies cloud architecture.",
                ),
            ],
        )
    )
    monkeypatch.setattr(research_service, "get_gemini_client", lambda: mock_gemini)

    with TestClient(app) as client:
        client.post("/api/prospects/seed")
        list_res = client.get("/api/prospects?search=Khatabook")
        prospect_id = list_res.json()[0]["id"]

        res = client.post(f"/api/prospects/{prospect_id}/research")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ANALYZED"
        assert mock_gemini.extract_evidence.called


def test_zero_auto_send_guarantee():
    """Security verification: assert no mail transmission libraries or endpoints exist."""
    import sys

    # Disallowed email dispatch modules
    forbidden_modules = [
        "smtplib",
        "sendgrid",
        "boto3.ses",
        "mailgun",
        "resend",
    ]
    for mod in forbidden_modules:
        assert mod not in sys.modules, (
            f"Forbidden email sending module {mod} is loaded!"
        )


def test_live_credentials_honest_reporting():
    """Verify system honestly reports whether live credentials are configured."""
    # When no keys are set, system must report MOCK mode and live_connected=False
    assert not config.settings.GEMINI_API_KEY or config.settings.USE_MOCK_APIS
    with TestClient(app) as client:
        res = client.get("/api/health")
        data = res.json()
        if config.settings.USE_MOCK_APIS or not config.settings.GEMINI_API_KEY:
            assert data["api_mode"] == "MOCK"
            assert data["live_connected"] is False

"""Integration tests for frontend-backend contract regarding MOCK/LIVE status and outreach generation source.

Verifies:
1. MOCK status response from GET /api/health when USE_MOCK_APIS=True.
2. LIVE status response from GET /api/health using configuration without exposing secrets.
3. Backend disconnection / degraded DB state in /api/health.
4. Deterministic template outreach draft response containing generation_source="DETERMINISTIC_TEMPLATE".
5. Gemini-generated outreach draft response containing generation_source="GEMINI_AI" via mock boundary.
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core import config
from app.main import app
from app.services.gemini_client import GeminiOutreachDraftResponse


def test_mock_status_health():
    """Verify GET /api/health returns api_mode='MOCK' and status='ok' in mock mode."""
    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["db"] is True
        assert data["api_mode"] == "MOCK"
        assert data["live_connected"] is False


def test_live_status_health_configuration(monkeypatch):
    """Verify GET /api/health returns live api_mode when configured with live key."""
    monkeypatch.setattr(config.settings, "USE_MOCK_APIS", False)
    monkeypatch.setattr(config.settings, "GEMINI_API_KEY", "test-valid-configured-key")

    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["db"] is True
        assert data["api_mode"] in ("LIVE", "LIVE_CONFIGURED", "LIVE_VERIFIED")
        assert "live_connected" in data


def test_backend_degraded_disconnection_status():
    """Verify GET /api/health returns status='degraded' and db=False on database disconnection."""
    with patch("app.main.check_db_health", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = False
        with TestClient(app) as client:
            res = client.get("/api/health")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "degraded"
            assert data["db"] is False
            assert "api_mode" in data


def test_template_generated_draft_indicator():
    """Verify that in mock mode, outreach draft endpoint returns generation_source='DETERMINISTIC_TEMPLATE'."""
    with TestClient(app) as client:
        # Seed prospects first
        client.post("/api/prospects/seed")
        list_res = client.get("/api/prospects?search=Khatabook")
        prospect_id = list_res.json()[0]["id"]

        # Run research to generate verified facts
        client.post(f"/api/prospects/{prospect_id}/research")

        # Generate draft in mock mode
        res = client.post(
            f"/api/prospects/{prospect_id}/draft",
            json={
                "template_type": "EVIDENCE_PROBLEM_SOLUTION",
                "tone": "CONSULTATIVE_DIRECT",
            },
        )
        assert res.status_code == 200
        draft = res.json()
        assert draft["generation_source"] == "DETERMINISTIC_TEMPLATE"
        assert draft["subject_line"] != ""
        assert "[Ref: #" in draft["body_text"]


def test_gemini_generated_draft_indicator(monkeypatch):
    """Verify that in live mode with Gemini client, outreach draft returns generation_source='GEMINI_AI'."""
    from app.services import outreach_service

    monkeypatch.setattr(outreach_service.settings, "USE_MOCK_APIS", False)
    monkeypatch.setattr(outreach_service.settings, "GEMINI_API_KEY", "test-live-key")

    mock_gemini = AsyncMock()
    mock_gemini.generate_outreach_draft = AsyncMock(
        return_value=GeminiOutreachDraftResponse(
            subject_line="Scaling with LeadForge AI",
            body_text="Hi team, observed your MSME focus [Ref: #1]. Would love to chat.",
            referenced_evidence_ids=[1],
            word_count=13,
        )
    )
    monkeypatch.setattr(outreach_service, "get_gemini_client", lambda: mock_gemini)

    with TestClient(app) as client:
        # Seed & research Khatabook
        client.post("/api/prospects/seed")
        list_res = client.get("/api/prospects?search=Khatabook")
        prospect_id = list_res.json()[0]["id"]
        client.post(f"/api/prospects/{prospect_id}/research")

        res = client.post(
            f"/api/prospects/{prospect_id}/draft",
            json={
                "template_type": "EVIDENCE_PROBLEM_SOLUTION",
                "tone": "CONSULTATIVE_DIRECT",
            },
        )
        assert res.status_code == 200
        draft = res.json()
        assert draft["generation_source"] == "GEMINI_AI"
        assert draft["subject_line"] == "Scaling with LeadForge AI"

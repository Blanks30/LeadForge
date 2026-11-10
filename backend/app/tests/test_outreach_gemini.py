"""Tests for Gemini-backed outreach draft generation (AGENTS.md §4.2).

Covers:
- GeminiOutreachDraftResponse schema validation
- generate_outreach_draft method: success path, schema violation, empty evidence guard
- outreach_service: live Gemini path, template fallback (mock mode, no key, Gemini error)
- api_mode indicator in /api/health response
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.gemini_client import (
    GeminiClient,
    GeminiConfigError,
    GeminiMalformedResponseError,
    GeminiNetworkError,
    GeminiOutreachDraftResponse,
    GeminiRateLimitError,
)

# ---------------------------------------------------------------------------
# Shared Fixtures
# ---------------------------------------------------------------------------

VALID_OUTREACH_PAYLOAD = {
    "subject_line": "Scaling Khatabook's SMB SaaS strategy",
    "body_text": (
        "Hi Khatabook team,\n\n"
        "I noticed that you explicitly target Indian MSMEs and Kirana store owners [Ref: #1]. "
        "Your transparent ₹499/month pricing makes high-conversion outreach very relevant [Ref: #2].\n\n"
        "We help Indian B2B SaaS teams accelerate qualified pipeline. Open for a 10-minute call?\n\n"
        "Best regards,\nAarav Mehta | LeadForge"
    ),
    "referenced_evidence_ids": [1, 2],
    "word_count": 55,
}

GEMINI_OUTREACH_SUCCESS_ENVELOPE = {
    "candidates": [
        {
            "content": {
                "role": "model",
                "parts": [{"text": json.dumps(VALID_OUTREACH_PAYLOAD)}],
            },
            "finishReason": "STOP",
        }
    ]
}

SAMPLE_EVIDENCE = [
    {
        "id": 1,
        "category": "SMB_FOCUS",
        "rubric_criterion": "MSME_EXPLICIT_FOCUS",
        "claim_text": "Explicitly targets Indian Kiranas and micro/small retailers.",
        "exact_quote": "Khatabook helps Indian MSMEs and Kirana store owners record transactions",
        "epistemic_status": "FACT",
        "confidence_score": 1.0,
    },
    {
        "id": 2,
        "category": "SMB_FOCUS",
        "rubric_criterion": "INR_PRICING",
        "claim_text": "Transparent software pricing in Indian Rupees (INR).",
        "exact_quote": "Starter Plan: ₹499/month billed annually.",
        "epistemic_status": "FACT",
        "confidence_score": 1.0,
    },
]


def _make_response(status_code, body):
    if isinstance(body, dict):
        content = json.dumps(body).encode()
        headers = {"content-type": "application/json"}
    else:
        content = body.encode()
        headers = {"content-type": "text/plain"}
    return httpx.Response(status_code=status_code, content=content, headers=headers)


def _mock_httpx_client(mock_post):
    mock_instance = AsyncMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    mock_instance.post = mock_post
    return mock_instance


def _client_with_key(key="fake-api-key-for-testing"):
    return GeminiClient(api_key=key, model="gemini-1.5-flash")


# ---------------------------------------------------------------------------
# GeminiOutreachDraftResponse schema
# ---------------------------------------------------------------------------


def test_outreach_draft_response_valid_payload():
    """GeminiOutreachDraftResponse validates a fully formed payload."""
    response = GeminiOutreachDraftResponse.model_validate(VALID_OUTREACH_PAYLOAD)
    assert response.subject_line.startswith("Scaling")
    assert "[Ref: #1]" in response.body_text
    assert response.referenced_evidence_ids == [1, 2]
    assert response.word_count == 55


def test_outreach_draft_response_missing_subject_raises():
    """GeminiOutreachDraftResponse rejects payload without subject_line."""
    from pydantic import ValidationError

    bad = {k: v for k, v in VALID_OUTREACH_PAYLOAD.items() if k != "subject_line"}
    with pytest.raises(ValidationError):
        GeminiOutreachDraftResponse.model_validate(bad)


def test_outreach_draft_response_missing_word_count_raises():
    """GeminiOutreachDraftResponse rejects payload without word_count."""
    from pydantic import ValidationError

    bad = {k: v for k, v in VALID_OUTREACH_PAYLOAD.items() if k != "word_count"}
    with pytest.raises(ValidationError):
        GeminiOutreachDraftResponse.model_validate(bad)


def test_outreach_draft_response_empty_evidence_ids_allowed():
    """GeminiOutreachDraftResponse allows empty referenced_evidence_ids list."""
    payload = {**VALID_OUTREACH_PAYLOAD, "referenced_evidence_ids": []}
    response = GeminiOutreachDraftResponse.model_validate(payload)
    assert response.referenced_evidence_ids == []


# ---------------------------------------------------------------------------
# GeminiClient.generate_outreach_draft — success path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_outreach_draft_success():
    """generate_outreach_draft returns parsed GeminiOutreachDraftResponse on 200."""
    mock_post = AsyncMock(
        return_value=_make_response(200, GEMINI_OUTREACH_SUCCESS_ENVELOPE)
    )
    with patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)):
        result = await _client_with_key().generate_outreach_draft(
            company_name="Khatabook",
            approved_evidence=SAMPLE_EVIDENCE,
        )
    assert isinstance(result, GeminiOutreachDraftResponse)
    assert result.subject_line == "Scaling Khatabook's SMB SaaS strategy"
    assert "[Ref: #1]" in result.body_text
    assert result.referenced_evidence_ids == [1, 2]


@pytest.mark.asyncio
async def test_generate_outreach_draft_raises_config_error_without_key():
    """generate_outreach_draft raises GeminiConfigError when no API key set."""
    client = GeminiClient(api_key="", model="gemini-1.5-flash")
    with pytest.raises(GeminiConfigError, match="GEMINI_API_KEY"):
        await client.generate_outreach_draft(
            company_name="Khatabook",
            approved_evidence=SAMPLE_EVIDENCE,
        )


@pytest.mark.asyncio
async def test_generate_outreach_draft_raises_malformed_error_on_empty_evidence():
    """generate_outreach_draft raises GeminiMalformedResponseError with empty evidence."""
    with pytest.raises(GeminiMalformedResponseError, match="empty evidence"):
        await _client_with_key().generate_outreach_draft(
            company_name="Khatabook",
            approved_evidence=[],
        )


@pytest.mark.asyncio
async def test_generate_outreach_draft_schema_violation():
    """generate_outreach_draft raises GeminiMalformedResponseError on schema violation."""
    bad_payload = {"subject_line": "Test", "body_text": "Hi"}  # missing word_count
    envelope = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": json.dumps(bad_payload)}]}}
        ]
    }
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="outreach schema"),
    ):
        await _client_with_key().generate_outreach_draft(
            company_name="Khatabook",
            approved_evidence=SAMPLE_EVIDENCE,
        )


@pytest.mark.asyncio
async def test_generate_outreach_draft_rate_limit():
    """generate_outreach_draft raises GeminiRateLimitError on 429."""
    mock_post = AsyncMock(return_value=_make_response(429, {"error": "QUOTA"}))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiRateLimitError),
    ):
        await _client_with_key().generate_outreach_draft(
            company_name="Khatabook",
            approved_evidence=SAMPLE_EVIDENCE,
        )


@pytest.mark.asyncio
async def test_generate_outreach_draft_network_error():
    """generate_outreach_draft raises GeminiNetworkError on connection failure."""
    mock_post = AsyncMock(side_effect=httpx.ConnectError("refused"))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiNetworkError),
    ):
        await _client_with_key().generate_outreach_draft(
            company_name="Khatabook",
            approved_evidence=SAMPLE_EVIDENCE,
        )


# ---------------------------------------------------------------------------
# _build_outreach_prompt_payload — API key not in payload
# ---------------------------------------------------------------------------


def test_outreach_prompt_payload_does_not_contain_api_key():
    """API key must never appear in the outreach prompt payload."""
    secret = "ultra-secret-outreach-key-xyz"
    client = GeminiClient(api_key=secret, model="gemini-1.5-flash")
    payload = client._build_outreach_prompt_payload(
        company_name="Khatabook",
        approved_evidence=SAMPLE_EVIDENCE,
        tone="CONSULTATIVE_DIRECT",
    )
    assert secret not in json.dumps(payload)


def test_outreach_prompt_payload_contains_evidence_ids():
    """Outreach prompt should embed evidence IDs for Gemini to cite."""
    client = _client_with_key()
    payload = client._build_outreach_prompt_payload(
        company_name="Khatabook",
        approved_evidence=SAMPLE_EVIDENCE,
    )
    prompt_text = json.dumps(payload)
    assert "Khatabook" in prompt_text
    assert "APPROVED EVIDENCE LIST" in prompt_text


# ---------------------------------------------------------------------------
# outreach_service — template fallback paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_outreach_service_persists_generation_source(db_session, monkeypatch):
    """Verify that outreach_service tags drafts with correct generation_source."""
    from app.db.models import EvidenceItem, IcpProfile, Prospect
    from app.services import outreach_service

    # Create dummy prospect with a FACT
    icp = IcpProfile(vertical="B2B SaaS")
    db_session.add(icp)
    await db_session.flush()

    prospect = Prospect(
        icp_id=icp.id,
        company_name="SourceTest",
        website_url="https://sourcetest.in",
        domain="sourcetest.in",
    )
    db_session.add(prospect)
    await db_session.flush()

    fact = EvidenceItem(
        prospect_id=prospect.id,
        category="SMB_FOCUS",
        claim_text="Active SMB focus",
        exact_quote="We help small shops",
        epistemic_status="FACT",
    )
    db_session.add(fact)
    await db_session.commit()

    # In mock mode, generation_source should be DETERMINISTIC_TEMPLATE
    monkeypatch.setattr(outreach_service.settings, "USE_MOCK_APIS", True)
    draft_template = await outreach_service.generate_outreach_draft(
        prospect.id, db_session
    )
    assert draft_template.generation_source == "DETERMINISTIC_TEMPLATE"

    # In live mode with mocked Gemini client, generation_source should be GEMINI_AI
    monkeypatch.setattr(outreach_service.settings, "USE_MOCK_APIS", False)
    monkeypatch.setattr(outreach_service.settings, "GEMINI_API_KEY", "mock-key")

    mock_gemini = AsyncMock()
    mock_gemini.generate_outreach_draft = AsyncMock(
        return_value=GeminiOutreachDraftResponse(
            subject_line="AI Subject",
            body_text="AI Body text [Ref: #1]",
            referenced_evidence_ids=[fact.id],
            word_count=5,
        )
    )
    monkeypatch.setattr(outreach_service, "get_gemini_client", lambda: mock_gemini)

    draft_gemini = await outreach_service.generate_outreach_draft(
        prospect.id, db_session
    )
    assert draft_gemini.generation_source == "GEMINI_AI"


# ---------------------------------------------------------------------------
# /api/health — api_mode indicator
# ---------------------------------------------------------------------------


def test_health_includes_api_mode_mock():
    """GET /api/health returns api_mode=MOCK when USE_MOCK_APIS=True."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert "api_mode" in data
        # Default settings have USE_MOCK_APIS=True → expect MOCK
        assert data["api_mode"] == "MOCK"


def test_health_api_mode_live_when_key_set(monkeypatch):
    """GET /api/health returns live api_mode when USE_MOCK_APIS=False and key is set."""
    from fastapi.testclient import TestClient

    from app.core import config
    from app.main import app

    monkeypatch.setattr(config.settings, "USE_MOCK_APIS", False)
    monkeypatch.setattr(config.settings, "GEMINI_API_KEY", "test-live-key")

    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["api_mode"] in ("LIVE", "LIVE_CONFIGURED", "LIVE_VERIFIED")

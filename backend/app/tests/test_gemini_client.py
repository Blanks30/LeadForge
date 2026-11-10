import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.gemini_client import (
    DEFAULT_FALLBACK_MODEL,
    SUPPORTED_GEMINI_MODELS,
    GeminiAuthError,
    GeminiClient,
    GeminiConfigError,
    GeminiError,
    GeminiExtractionResponse,
    GeminiMalformedResponseError,
    GeminiModelNotFoundError,
    GeminiNetworkError,
    GeminiRateLimitError,
    GeminiUnavailableError,
    resolve_model_name,
)
from app.services.research_service import verify_grounding

VALID_EXTRACTION_PAYLOAD = {
    "company_name": "TestCo",
    "hq_location": "Bengaluru, India",
    "employee_range": "50-200",
    "evidence_items": [
        {
            "category": "SMB_FOCUS",
            "rubric_criterion": "MSME_EXPLICIT_FOCUS",
            "claim_text": "TestCo targets Indian MSMEs.",
            "exact_quote": "Built for Indian MSMEs and Kirana stores.",
            "epistemic_status": "FACT",
            "confidence_score": 1.0,
            "source_url": "https://testco.in",
            "publication_date": None,
            "gemini_reasoning": None,
        },
        {
            "category": "SAAS_MODEL",
            "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
            "claim_text": "Cloud-hosted SaaS platform.",
            "exact_quote": None,
            "epistemic_status": "INFERENCE",
            "confidence_score": 0.85,
            "source_url": None,
            "publication_date": None,
            "gemini_reasoning": "The homepage references a web app dashboard.",
        },
    ],
}

GEMINI_SUCCESS_ENVELOPE = {
    "candidates": [
        {
            "content": {
                "role": "model",
                "parts": [{"text": json.dumps(VALID_EXTRACTION_PAYLOAD)}],
            },
            "finishReason": "STOP",
        }
    ]
}

SAMPLE_SOURCES = [
    {
        "url": "https://testco.in",
        "page_type": "HOMEPAGE",
        "raw_text_snippet": "Built for Indian MSMEs and Kirana stores.",
    }
]


def _make_response(status_code, body):
    if isinstance(body, dict):
        content = json.dumps(body).encode()
        headers = {"content-type": "application/json"}
    else:
        content = body.encode()
        headers = {"content-type": "text/plain"}
    return httpx.Response(status_code=status_code, content=content, headers=headers)


def _client_with_key(key="fake-api-key-for-testing"):
    return GeminiClient(api_key=key, model="gemini-1.5-flash")


def _mock_httpx_client(mock_post):
    mock_instance = AsyncMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    mock_instance.post = mock_post
    return mock_instance


# --- resolve_model_name ---


def test_resolve_known_models():
    for model in SUPPORTED_GEMINI_MODELS:
        assert resolve_model_name(model) == model


def test_resolve_strips_models_prefix():
    assert resolve_model_name("models/gemini-1.5-flash") == "gemini-1.5-flash"


def test_resolve_unknown_model_fallback():
    assert resolve_model_name("gemini-99.0-nonexistent") == DEFAULT_FALLBACK_MODEL


def test_resolve_none_or_empty_fallback():
    assert resolve_model_name(None) == DEFAULT_FALLBACK_MODEL
    assert resolve_model_name("") == DEFAULT_FALLBACK_MODEL


# --- No API key ---


@pytest.mark.asyncio
async def test_raises_config_error_when_no_api_key():
    client = GeminiClient(api_key="", model="gemini-1.5-flash")
    with pytest.raises(GeminiConfigError, match="GEMINI_API_KEY"):
        await client.extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Empty sources ---


@pytest.mark.asyncio
async def test_raises_malformed_error_on_empty_sources():
    client = _client_with_key()
    with pytest.raises(GeminiMalformedResponseError, match="empty sources"):
        await client.extract_evidence("TestCo", [])


# --- Valid 200 response ---


@pytest.mark.asyncio
async def test_valid_200_response_parsed_correctly():
    mock_post = AsyncMock(return_value=_make_response(200, GEMINI_SUCCESS_ENVELOPE))
    with patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)):
        result = await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)
    assert isinstance(result, GeminiExtractionResponse)
    assert result.company_name == "TestCo"
    assert result.hq_location == "Bengaluru, India"
    assert len(result.evidence_items) == 2
    assert result.evidence_items[0].epistemic_status == "FACT"
    assert result.evidence_items[1].epistemic_status == "INFERENCE"
    assert result.evidence_items[1].gemini_reasoning is not None


# --- Markdown fence stripping ---


@pytest.mark.asyncio
async def test_valid_response_with_backtick_json_fence():
    # Build the code fence string without backtick literals (avoids shell escaping issues)
    bt = chr(96) * 3
    fenced = bt + "json\n" + json.dumps(VALID_EXTRACTION_PAYLOAD) + "\n" + bt
    envelope = {
        "candidates": [{"content": {"role": "model", "parts": [{"text": fenced}]}}]
    }
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)):
        result = await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)
    assert result.company_name == "TestCo"


# --- Authentication failures ---


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [401, 403])
async def test_auth_error_on_4xx(status_code):
    mock_post = AsyncMock(return_value=_make_response(status_code, {"error": "UNAUTH"}))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiAuthError, match="authentication failed"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Rate limiting ---


@pytest.mark.asyncio
async def test_rate_limit_error_on_429():
    mock_post = AsyncMock(return_value=_make_response(429, {"error": "RATE_LIMIT"}))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiRateLimitError, match="rate limit"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Service unavailable ---


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
async def test_unavailable_error_on_5xx(status_code):
    mock_post = AsyncMock(
        return_value=_make_response(status_code, "Internal Server Error")
    )
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiUnavailableError, match="unavailable"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Model not found ---


@pytest.mark.asyncio
async def test_model_not_found_on_404():
    mock_post = AsyncMock(return_value=_make_response(404, {"error": "NOT_FOUND"}))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiModelNotFoundError, match="not found"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Unexpected HTTP status ---


@pytest.mark.asyncio
async def test_generic_error_on_unexpected_status():
    mock_post = AsyncMock(return_value=_make_response(418, "Teapot"))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiError),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Timeout ---


@pytest.mark.asyncio
async def test_timeout_raises_network_error():
    mock_post = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiNetworkError, match="timed out"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Connection error ---


@pytest.mark.asyncio
async def test_connection_error_raises_network_error():
    mock_post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiNetworkError, match="network connection failure"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Malformed responses ---


@pytest.mark.asyncio
async def test_non_json_body_raises_malformed_error():
    mock_post = AsyncMock(return_value=_make_response(200, "This is not JSON!"))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="non-JSON"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


@pytest.mark.asyncio
async def test_missing_candidates_raises_malformed_error():
    body = {"candidates": [], "promptFeedback": {"blockReason": "SAFETY"}}
    mock_post = AsyncMock(return_value=_make_response(200, body))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="no candidates"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


@pytest.mark.asyncio
async def test_missing_parts_raises_malformed_error():
    envelope = {"candidates": [{"content": {"role": "model", "parts": []}}]}
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="no text parts"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


@pytest.mark.asyncio
async def test_invalid_json_in_text_part():
    envelope = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": "{bad json!"}]}}
        ]
    }
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="Failed to parse"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


@pytest.mark.asyncio
async def test_schema_violation_missing_company_name():
    bad = {"evidence_items": []}
    envelope = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": json.dumps(bad)}]}}
        ]
    }
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="violated schema"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


@pytest.mark.asyncio
async def test_evidence_item_missing_required_fields():
    bad = {
        "company_name": "TestCo",
        "evidence_items": [{"category": "SMB_FOCUS", "claim_text": "Does something"}],
    }
    envelope = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": json.dumps(bad)}]}}
        ]
    }
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with (
        patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)),
        pytest.raises(GeminiMalformedResponseError, match="violated schema"),
    ):
        await _client_with_key().extract_evidence("TestCo", SAMPLE_SOURCES)


# --- Endpoint URL ---


def test_endpoint_url_uses_model_name():
    client = GeminiClient(api_key="key", model="gemini-2.0-flash")
    assert "gemini-2.0-flash" in client.endpoint_url
    assert client.endpoint_url.endswith(":generateContent")


def test_endpoint_url_override():
    override = "https://custom.endpoint/v1/generate"
    client = GeminiClient(
        api_key="key", model="gemini-1.5-flash", endpoint_override=override
    )
    assert client.endpoint_url == override


# --- Security: API key not in prompt payload ---


def test_api_key_not_in_prompt_payload():
    secret = "super-secret-api-key-abc123"
    client = GeminiClient(api_key=secret, model="gemini-1.5-flash")
    payload = client._build_prompt_payload("TestCo", SAMPLE_SOURCES)
    assert secret not in json.dumps(payload)


# --- Grounding verification ---


def test_grounding_passes_for_verbatim_substring():
    source = "Built for Indian MSMEs and Kirana stores. Plans from INR499."
    assert verify_grounding("Built for Indian MSMEs and Kirana stores.", source) is True


def test_grounding_passes_case_insensitive():
    assert verify_grounding("built for indian msmes", "BUILT FOR INDIAN MSMES") is True


def test_grounding_passes_whitespace_normalised():
    assert (
        verify_grounding("Plans start at INR499.", "Plans  start  at  INR499.") is True
    )


def test_grounding_fails_for_fabricated_quote():
    source = "Built for Indian MSMEs and Kirana stores."
    assert verify_grounding("We serve over 10 million Indian shops", source) is False


def test_grounding_fails_for_empty_quote():
    source = "Built for Indian MSMEs and Kirana stores."
    assert verify_grounding(None, source) is False
    assert verify_grounding("", source) is False


def test_grounding_fails_for_empty_source():
    assert verify_grounding("Starter Plan INR499/month", None) is False
    assert verify_grounding("Starter Plan INR499/month", "") is False


def test_grounding_fails_both_empty():
    assert verify_grounding(None, None) is False
    assert verify_grounding("", "") is False


# --- Grounding: hallucination downgrade in research pipeline ---


def test_grounding_quote_not_in_source_text_returns_false():
    source = "This is a real sentence about Khatabook."
    hallucinated = "We are used by 50 million merchants worldwide"
    assert verify_grounding(hallucinated, source) is False


# --- Mock mode independence ---


@pytest.mark.asyncio
async def test_mock_mode_does_not_call_gemini_api(monkeypatch):
    from app.services import research_service
    from app.services.gemini_client import GeminiClient as GC

    extract_mock = AsyncMock()
    monkeypatch.setattr(GC, "extract_evidence", extract_mock)
    monkeypatch.setattr(research_service.settings, "USE_MOCK_APIS", True)
    from app.services.tinyfish_client import MockTinyFishClient

    crawler = MockTinyFishClient()
    payload = await crawler.crawl_prospect("khatabook.com", "https://khatabook.com")
    assert payload["provider"] == "MOCK_ADAPTER"
    assert len(payload["evidence_items"]) > 0
    extract_mock.assert_not_called()


# --- Empty evidence items ---


@pytest.mark.asyncio
async def test_valid_response_with_empty_evidence_items():
    payload = {
        "company_name": "Emptyco",
        "hq_location": None,
        "employee_range": None,
        "evidence_items": [],
    }
    envelope = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": json.dumps(payload)}]}}
        ]
    }
    mock_post = AsyncMock(return_value=_make_response(200, envelope))
    with patch("httpx.AsyncClient", return_value=_mock_httpx_client(mock_post)):
        result = await _client_with_key().extract_evidence("EmptyCo", SAMPLE_SOURCES)
    assert result.company_name == "Emptyco"
    assert result.evidence_items == []

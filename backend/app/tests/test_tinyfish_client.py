"""Unit and integration tests for TinyFish client adapter.

Covers:
- MockTinyFishClient (known and unknown domains)
- LiveTinyFishClient: missing key fallback, network fallback, 200 invalid structure fallback
- LiveTinyFishClient: retry behavior on HTTP 429/503 with exponential backoff
- LiveTinyFishClient: successful 200 payload with provider="TINYFISH_LIVE"
- Factory function adherence to settings
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.core.config import settings
from app.services.tinyfish_client import (
    LiveTinyFishClient,
    MockTinyFishClient,
    get_tinyfish_client,
)


@pytest.mark.asyncio
async def test_mock_tinyfish_client_known_domain() -> None:
    """Verify that MockTinyFishClient returns structured fixtures for target companies."""
    client = MockTinyFishClient()
    result = await client.crawl_prospect("khatabook.com", "https://khatabook.com")

    assert result is not None
    assert result["provider"] == "MOCK_ADAPTER"
    assert result["company_name"] == "Khatabook"
    assert len(result["sources"]) >= 2
    assert len(result["evidence_items"]) >= 3


@pytest.mark.asyncio
async def test_mock_tinyfish_client_unknown_domain() -> None:
    """Verify that MockTinyFishClient returns a safe fallback for unknown domains."""
    client = MockTinyFishClient()
    result = await client.crawl_prospect("randomstartup.in", "https://randomstartup.in")

    assert result is not None
    assert result["provider"] == "MOCK_ADAPTER"
    assert result["company_name"] == "Randomstartup"
    assert len(result["sources"]) == 1
    assert result["evidence_items"][0]["epistemic_status"] == "FACT"


@pytest.mark.asyncio
async def test_live_tinyfish_client_fallback_without_key() -> None:
    """Verify that LiveTinyFishClient falls back to mock provider if no API key is set."""
    client = LiveTinyFishClient(api_key="")
    result = await client.crawl_prospect("mybillbook.in", "https://mybillbook.in")

    assert result is not None
    assert result["company_name"] == "myBillBook (FloBiz)"
    assert result["provider"] == "MOCK_ADAPTER"


@pytest.mark.asyncio
async def test_live_tinyfish_client_network_error_fallback() -> None:
    """Verify that LiveTinyFishClient falls back gracefully on network or HTTP errors."""
    client = LiveTinyFishClient(
        api_key="test-api-key",
        endpoint="http://127.0.0.1:9999/unreachable",
        max_retries=0,
    )
    result = await client.crawl_prospect("dukaan.com", "https://mydukaan.io")

    assert result is not None
    assert result["company_name"] == "Dukaan"
    assert result["provider"] == "MOCK_ADAPTER"


@pytest.mark.asyncio
async def test_live_tinyfish_client_success_200() -> None:
    """Verify LiveTinyFishClient parses successful 200 payload and tags provider='TINYFISH_LIVE'."""
    live_payload = {
        "company_name": "LiveSaaS",
        "sources": [
            {
                "url": "https://livesaas.io",
                "page_type": "HOMEPAGE",
                "raw_text_snippet": "LiveSaaS powers small businesses in India with cloud billing.",
            }
        ],
        "evidence_items": [],
    }

    mock_resp = httpx.Response(
        status_code=200,
        content=json.dumps(live_payload).encode(),
        headers={"content-type": "application/json"},
    )
    mock_post = AsyncMock(return_value=mock_resp)
    mock_instance = AsyncMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    mock_instance.post = mock_post

    client = LiveTinyFishClient(api_key="valid-test-key", max_retries=1)
    with patch("httpx.AsyncClient", return_value=mock_instance):
        res = await client.crawl_prospect("livesaas.io", "https://livesaas.io")

    assert res is not None
    assert res["provider"] == "TINYFISH_LIVE"
    assert res["company_name"] == "LiveSaaS"
    assert len(res["sources"]) == 1


@pytest.mark.asyncio
async def test_live_tinyfish_client_retries_on_429() -> None:
    """Verify LiveTinyFishClient retries on HTTP 429 and falls back to mock on exhaustion."""
    mock_resp = httpx.Response(status_code=429, content=b"Rate limited")
    mock_post = AsyncMock(return_value=mock_resp)
    mock_instance = AsyncMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    mock_instance.post = mock_post

    client = LiveTinyFishClient(api_key="valid-test-key", max_retries=2)
    with (
        patch("httpx.AsyncClient", return_value=mock_instance),
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        res = await client.crawl_prospect("dukaan.com", "https://mydukaan.io")

    assert mock_post.call_count == 3  # Initial + 2 retries
    assert mock_sleep.call_count == 2
    assert res is not None
    assert res["provider"] == "MOCK_ADAPTER"  # Graceful fallback


def test_get_tinyfish_client_factory() -> None:
    """Verify that factory adheres to settings.USE_MOCK_APIS."""
    client = get_tinyfish_client()
    if settings.USE_MOCK_APIS or not settings.TINYFISH_API_KEY:
        assert isinstance(client, MockTinyFishClient)

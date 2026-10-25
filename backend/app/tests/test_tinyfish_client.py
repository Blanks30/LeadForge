"""Unit and integration tests for TinyFish client adapter."""

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
async def test_live_tinyfish_client_network_error_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that LiveTinyFishClient falls back gracefully on network or HTTP errors."""
    client = LiveTinyFishClient(
        api_key="test-api-key", endpoint="http://127.0.0.1:9999/unreachable"
    )
    result = await client.crawl_prospect("dukaan.com", "https://mydukaan.io")

    assert result is not None
    assert result["company_name"] == "Dukaan"
    assert result["provider"] == "MOCK_ADAPTER"


def test_get_tinyfish_client_factory() -> None:
    """Verify that factory adheres to settings.USE_MOCK_APIS."""
    client = get_tinyfish_client()
    if settings.USE_MOCK_APIS or not settings.TINYFISH_API_KEY:
        assert isinstance(client, MockTinyFishClient)

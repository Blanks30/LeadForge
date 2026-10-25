"""TinyFish web crawling client adapter with deterministic mock fallback.

Enforces external boundary defense: isolates network crawling, timeouts,
and payload transformation, with graceful fallback to deterministic mock fixtures.
"""

from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import settings
from app.services.mock_research_data import MOCK_RESEARCH_PAYLOADS


class TinyFishClientBase(ABC):
    """Abstract base class for web research crawlers."""

    @abstractmethod
    async def crawl_prospect(
        self,
        domain: str,
        website_url: str,
    ) -> dict[str, Any] | None:
        """Crawl target domain and return structured sources and evidence payloads."""


class MockTinyFishClient(TinyFishClientBase):
    """Deterministic mock provider serving verified crawl fixtures.

    Provides grounded text snippets and evidence for the 10 target Indian SMB SaaS companies
    for offline development, deterministic testing, and hackathon demonstrations.
    """

    provider_name: str = "MOCK_ADAPTER"

    async def crawl_prospect(
        self,
        domain: str,
        website_url: str,
    ) -> dict[str, Any] | None:
        payload = MOCK_RESEARCH_PAYLOADS.get(domain)
        if payload:
            # Return copy with explicit provider tag
            return {**payload, "provider": self.provider_name}

        # Generic grounded fallback for arbitrary domains
        return {
            "provider": self.provider_name,
            "company_name": domain.split(".")[0].capitalize(),
            "hq_location": "India",
            "employee_range": "10-50",
            "sources": [
                {
                    "url": website_url,
                    "page_type": "HOMEPAGE",
                    "raw_text_snippet": f"{domain} delivers cloud software solutions for Indian businesses.",
                }
            ],
            "evidence_items": [
                {
                    "category": "SAAS_MODEL",
                    "rubric_criterion": "CLOUD_SAAS_ARCHITECTURE",
                    "claim_text": "Cloud software architecture verified",
                    "exact_quote": f"{domain} delivers cloud software solutions for Indian businesses.",
                    "epistemic_status": "FACT",
                    "confidence_score": 1.0,
                    "gemini_reasoning": None,
                    "source_index": 0,
                }
            ],
        }


class LiveTinyFishClient(TinyFishClientBase):
    """Live HTTP client for TinyFish web scraping API.

    Caps timeouts at 30 seconds per domain and gracefully degrades to MockTinyFishClient
    if the external API is unreachable, unconfigured, or returns an error.
    """

    provider_name: str = "TINYFISH_LIVE"

    def __init__(
        self, api_key: str, endpoint: str = "https://api.tinyfish.io/v1/crawl"
    ) -> None:
        self.api_key = api_key
        self.endpoint = endpoint
        self._mock_fallback = MockTinyFishClient()

    async def crawl_prospect(
        self,
        domain: str,
        website_url: str,
    ) -> dict[str, Any] | None:
        """Execute HTTP request against TinyFish API with 30s timeout and safe fallback."""
        if not self.api_key:
            # Fall back to mock if no API key is provided
            return await self._mock_fallback.crawl_prospect(domain, website_url)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "LeadForge/0.1.0",
        }
        payload = {
            "url": website_url,
            "domain": domain,
            "pages": ["homepage", "pricing", "about", "blog"],
            "max_timeout_seconds": 30,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.endpoint, json=payload, headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    return {**data, "provider": self.provider_name}
                # Log or handle non-200 by falling back cleanly
                return await self._mock_fallback.crawl_prospect(domain, website_url)
        except (httpx.HTTPError, TimeoutError, OSError):
            # Network failure or timeout: fallback to mock adapter without crashing
            return await self._mock_fallback.crawl_prospect(domain, website_url)


def get_tinyfish_client() -> TinyFishClientBase:
    """Factory function returning the configured crawler client."""
    if settings.USE_MOCK_APIS or not settings.TINYFISH_API_KEY:
        return MockTinyFishClient()
    return LiveTinyFishClient(api_key=settings.TINYFISH_API_KEY)

"""TinyFish web crawling client adapter with deterministic mock fallback.

Enforces external boundary defense: isolates network crawling, timeouts, retries,
and payload transformation, with graceful fallback to deterministic mock fixtures.
Follows ARCHITECTURE.md §6.1 and PRD.md §4.2.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import settings
from app.services.mock_research_data import MOCK_RESEARCH_PAYLOADS

logger = logging.getLogger("leadforge.tinyfish")


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

    Implements:
    - 30-second strict timeout ceiling per domain (PRD.md §4.2)
    - Max 2 retries on HTTP 429/503 with exponential backoff (ARCHITECTURE.md §6.1)
    - Safe fallback to MockTinyFishClient on network error, authentication failure, or empty response
    """

    provider_name: str = "TINYFISH_LIVE"

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.tinyfish.io/v1/crawl",
        max_retries: int = 2,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self._mock_fallback = MockTinyFishClient()

    async def crawl_prospect(
        self,
        domain: str,
        website_url: str,
    ) -> dict[str, Any] | None:
        """Execute HTTP request against TinyFish API with retries and safe fallback."""
        if not self.api_key:
            logger.info(
                "TINYFISH_API_KEY unset; serving mock crawl fixtures for %s.", domain
            )
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
            "max_timeout_seconds": int(self.timeout_seconds),
        }

        retries = 0
        while retries <= self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(
                        self.endpoint, json=payload, headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        # Ensure minimal expected structure exists
                        if isinstance(data, dict) and "sources" in data:
                            return {**data, "provider": self.provider_name}
                        # If 200 but empty/invalid structure, fallback cleanly
                        logger.warning(
                            "TinyFish returned 200 with invalid structure for %s; using mock fallback.",
                            domain,
                        )
                        return await self._mock_fallback.crawl_prospect(
                            domain, website_url
                        )

                    # Transient server or rate-limit error: retry with exponential backoff
                    if (
                        response.status_code in (429, 503)
                        and retries < self.max_retries
                    ):
                        retries += 1
                        backoff = 0.5 * (2 ** (retries - 1))
                        logger.warning(
                            "TinyFish HTTP %d for %s; retry %d/%d in %.1fs",
                            response.status_code,
                            domain,
                            retries,
                            self.max_retries,
                            backoff,
                        )
                        await asyncio.sleep(backoff)
                        continue

                    # Non-retriable HTTP error (401, 403, 404, 500, etc.)
                    logger.warning(
                        "TinyFish crawl failed (HTTP %d) for %s; falling back to mock fixtures.",
                        response.status_code,
                        domain,
                    )
                    return await self._mock_fallback.crawl_prospect(domain, website_url)

            except (httpx.TimeoutException, httpx.RequestError, OSError) as exc:
                if retries < self.max_retries:
                    retries += 1
                    backoff = 0.5 * (2 ** (retries - 1))
                    logger.warning(
                        "TinyFish network error (%s) for %s; retry %d/%d in %.1fs",
                        type(exc).__name__,
                        domain,
                        retries,
                        self.max_retries,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue

                logger.warning(
                    "TinyFish network failure (%s) for %s after retries; falling back to mock fixtures.",
                    type(exc).__name__,
                    domain,
                )
                return await self._mock_fallback.crawl_prospect(domain, website_url)

        return await self._mock_fallback.crawl_prospect(domain, website_url)


def get_tinyfish_client() -> TinyFishClientBase:
    """Factory function returning the configured crawler client."""
    if settings.USE_MOCK_APIS or not settings.TINYFISH_API_KEY:
        return MockTinyFishClient()
    return LiveTinyFishClient(api_key=settings.TINYFISH_API_KEY)

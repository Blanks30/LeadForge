"""Tavily Search API client adapter for unrestricted internet search.

Executes general-purpose web queries against Tavily Search API without
pre-filtering, geographic locking, or appended keywords. Follows strict
boundary isolation and supports deterministic mock fallbacks for offline testing.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.search_schema import (
    SearchResponse,
    SearchResultItem,
    derive_candidate_company_name,
    extract_domain,
)

logger = logging.getLogger("leadforge.tavily")


class TavilyError(Exception):
    """Base exception for Tavily search operations."""


class TavilyConfigError(TavilyError):
    """Raised when Tavily API key is missing or misconfigured in live mode."""


class TavilyAuthError(TavilyError):
    """Raised when Tavily API rejects credentials (HTTP 401/403)."""


class TavilyRateLimitError(TavilyError):
    """Raised when Tavily API returns HTTP 429 Too Many Requests."""


class TavilyNetworkError(TavilyError):
    """Raised on connection timeout or network failure."""


class TavilyClient:
    """HTTP client for general-purpose web search via Tavily Search API."""

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str = "https://api.tavily.com/search",
        timeout_seconds: float = 20.0,
    ) -> None:
        self.api_key = (
            api_key if api_key is not None else settings.TAVILY_API_KEY
        ).strip()
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    async def search(
        self,
        query: str,
        max_results: int = 8,
    ) -> SearchResponse:
        """Execute a general-purpose web search.

        CRITICAL REQUIREMENT:
        The exact query is passed to Tavily without appending industry,
        geography, company, or SaaS keywords.
        """
        exact_query = query.strip()
        if not exact_query:
            raise ValueError("Query cannot be empty.")

        # Offline Mock Mode (e.g. during local tests or offline evaluation)
        if settings.USE_MOCK_APIS:
            return self._generate_mock_results(exact_query, max_results)

        # Live Mode: Verify API key presence
        if not self.api_key:
            logger.warning(
                "Tavily live search attempted without TAVILY_API_KEY configured."
            )
            raise TavilyConfigError(
                "TAVILY_API_KEY is not configured in backend environment. "
                "Please configure TAVILY_API_KEY in backend/.env to perform live internet searches."
            )

        payload: dict[str, Any] = {
            "api_key": self.api_key,
            "query": exact_query,  # Exact unmodified query
            "search_depth": "basic",
            "include_answer": False,
            "max_results": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code in (401, 403):
                    logger.error(
                        "Tavily API authentication failure (HTTP %d)",
                        response.status_code,
                    )
                    raise TavilyAuthError(
                        "Tavily API rejected authentication credentials. Check TAVILY_API_KEY."
                    )

                if response.status_code == 429:
                    logger.warning("Tavily API rate limit exceeded (HTTP 429)")
                    raise TavilyRateLimitError(
                        "Tavily search rate limit exceeded. Please retry in a few moments."
                    )

                if not response.is_success:
                    logger.error(
                        "Tavily API returned error HTTP %d: %s",
                        response.status_code,
                        response.text[:200],
                    )
                    raise TavilyError(
                        f"Tavily API request failed with HTTP status {response.status_code}."
                    )

                data = response.json()
                raw_results = data.get("results", [])

                items: list[SearchResultItem] = []
                for r in raw_results:
                    url = r.get("url", "")
                    title = r.get("title", "")
                    content = r.get("content", "")
                    score = r.get("score")
                    domain = extract_domain(url)
                    candidate_name = derive_candidate_company_name(title, domain)

                    items.append(
                        SearchResultItem(
                            title=title,
                            url=url,
                            content=content,
                            score=score,
                            domain=domain,
                            candidate_company_name=candidate_name,
                            is_company_candidate=bool(domain and len(domain) > 3),
                        )
                    )

                return SearchResponse(
                    query=exact_query,
                    results=items,
                    total_results=len(items),
                    provider="TAVILY_LIVE",
                    is_live=True,
                    message=None,
                )

        except TavilyError:
            raise
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError) as exc:
            logger.error(
                "Network error reaching Tavily API: %s (%s)", exc, type(exc).__name__
            )
            raise TavilyNetworkError(
                f"Failed to connect to Tavily search service: {exc}"
            ) from exc

    def _generate_mock_results(self, query: str, max_results: int) -> SearchResponse:
        """Deterministic mock search results for offline development and testing.

        Generates structured results matching any natural-language topic, clearly
        tagged with provider='MOCK_SEARCH' and is_live=False.
        """
        normalized = query.lower()

        # Topic-sensitive realistic fixtures
        if "ai agent" in normalized or "artificial intelligence" in normalized:
            fixtures = [
                {
                    "title": "AutoGPT - Open Source Autonomous AI Agents",
                    "url": "https://autogpt.net",
                    "content": "An open-source autonomous AI agent framework designed to break down and execute complex multi-step objectives autonomously.",
                    "score": 0.98,
                },
                {
                    "title": "CrewAI: Framework for Orchestrating Role-Playing AI Agents",
                    "url": "https://crewai.com",
                    "content": "CrewAI facilitates autonomous AI agent collaboration. Enable agents to work together seamlessly to tackle complex workflows.",
                    "score": 0.94,
                },
                {
                    "title": "LangChain - Agentic Workflows & Multi-Agent Architecture",
                    "url": "https://langchain.com",
                    "content": "Build context-aware, reasoning applications with LangChain's flexible agentic libraries and evaluation suites.",
                    "score": 0.91,
                },
            ]
        elif "cybersecurity" in normalized or "security" in normalized:
            fixtures = [
                {
                    "title": "Top Cybersecurity Trends and Threat Landscape Analysis",
                    "url": "https://cisa.gov/cybersecurity-trends",
                    "content": "Key cybersecurity trends including zero-trust architecture adoption, quantum-resistant encryption, and automated vulnerability scanning.",
                    "score": 0.96,
                },
                {
                    "title": "CrowdStrike Falcon - Cloud-Native Cybersecurity Platform",
                    "url": "https://crowdstrike.com",
                    "content": "Unified endpoint protection, threat intelligence, and automated incident response powered by cloud-native telemetry.",
                    "score": 0.92,
                },
            ]
        elif "linways" in normalized:
            fixtures = [
                {
                    "title": "Linways Technologies - Academic Management System & LMS",
                    "url": "https://linways.com",
                    "content": "Linways provides modern academic management software, accreditation tools, and learning management systems for higher education institutions.",
                    "score": 0.99,
                },
                {
                    "title": "Linways AMS Features - Outcome Based Education (OBE) Tools",
                    "url": "https://linways.com/features",
                    "content": "Automated NBA and NAAC accreditation calculation, student lifecycle management, and digital evaluation for universities.",
                    "score": 0.93,
                },
            ]
        elif "zoho" in normalized:
            fixtures = [
                {
                    "title": "Top Competitors & Alternatives to Zoho CRM in 2026",
                    "url": "https://softwareadvice.com/crm/zoho-alternatives",
                    "content": "Compare leading alternatives to Zoho CRM including HubSpot, Freshsales, Salesforce, and Pipedrive across pricing and SMB usability.",
                    "score": 0.95,
                },
                {
                    "title": "Freshworks vs Zoho: Comprehensive Software Suite Comparison",
                    "url": "https://freshworks.com/compare/zoho",
                    "content": "Detailed head-to-head comparison between Freshworks and Zoho covering CRM, customer support desk, and cloud ERP integrations.",
                    "score": 0.91,
                },
            ]
        else:
            # General-purpose internet search fallback for any user topic
            clean_q = query.replace('"', "").strip()
            fixtures = [
                {
                    "title": f"{clean_q} - Global Research Overview & Documentation",
                    "url": f"https://en.wikipedia.org/wiki/{clean_q.replace(' ', '_')}",
                    "content": f"Comprehensive exploration and factual overview regarding '{clean_q}', covering core principles, modern applications, and latest research updates.",
                    "score": 0.95,
                },
                {
                    "title": f"Latest Developments and Best Practices in {clean_q}",
                    "url": f"https://techradar.com/topics/{clean_q.lower().replace(' ', '-')}",
                    "content": f"Industry analysis, expert reviews, and comprehensive guides analyzing the latest advancements in {clean_q}.",
                    "score": 0.90,
                },
                {
                    "title": f"{clean_q} Technologies & Official Resources",
                    "url": f"https://github.com/topics/{clean_q.lower().replace(' ', '-')}",
                    "content": f"Curated open-source repositories, developer tools, and technology benchmarks relevant to {clean_q}.",
                    "score": 0.85,
                },
            ]

        results = [
            SearchResultItem(
                title=f["title"],
                url=f["url"],
                content=f["content"],
                score=f.get("score"),
                domain=extract_domain(f["url"]),
                candidate_company_name=derive_candidate_company_name(
                    f["title"], extract_domain(f["url"])
                ),
                is_company_candidate=bool(
                    extract_domain(f["url"]) and len(extract_domain(f["url"])) > 3
                ),
            )
            for f in fixtures[:max_results]
        ]

        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            provider="MOCK_SEARCH",
            is_live=False,
            message="Results generated via offline mock provider. Configure TAVILY_API_KEY in backend/.env for live web search.",
        )


def get_tavily_client() -> TavilyClient:
    """Factory helper returning a configured TavilyClient instance."""
    return TavilyClient()

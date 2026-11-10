"""Pydantic schemas for general-purpose internet search powered by Tavily."""

from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


def extract_domain(url: str) -> str:
    """Safely extract root domain from a URL."""
    try:
        parsed = urlparse(url.strip())
        host = parsed.hostname or parsed.netloc
        if ":" in host:
            host = host.split(":")[0]
        return host.lower().removeprefix("www.")
    except (ValueError, AttributeError):
        return ""


def derive_candidate_company_name(title: str, domain: str) -> str:
    """Infer candidate company name from title or root domain."""
    # If title has common delimiters like ' - ', ' | ', ' : '
    for sep in (" - ", " | ", " : ", " • "):
        if sep in title:
            candidate = title.split(sep)[0].strip()
            if candidate and len(candidate) <= 50:
                return candidate

    # Fallback to domain root capitalized
    if domain:
        parts = domain.split(".")
        if parts:
            name = parts[0]
            if len(name) > 1:
                return name.capitalize()

    return title[:40].strip()


class SearchResultItem(BaseModel):
    """Individual search result item returned from Tavily."""

    title: str = Field(description="Page title")
    url: str = Field(description="Direct URL to source")
    content: str = Field(description="Snippet or summary of page content")
    score: float | None = Field(
        default=None, description="Relevance score from search engine"
    )
    domain: str | None = Field(
        default=None, description="Normalized root domain of the URL"
    )
    candidate_company_name: str | None = Field(
        default=None,
        description="Suggested company name if user chooses to ingest this result into LeadForge",
    )
    is_company_candidate: bool = Field(
        default=True,
        description="Indicates whether this result is eligible to be added as a custom company",
    )

    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    """General-purpose internet search request.

    Accepts any natural-language topic or query without pre-filtering
    or appending industry/geography keywords.
    """

    query: str = Field(
        min_length=1,
        max_length=500,
        description="Unrestricted natural language query for general internet search",
    )
    max_results: int = Field(
        default=8,
        ge=1,
        le=20,
        description="Maximum search results to return",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Ensure search query is not blank."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Search query cannot be blank.")
        return cleaned


class SearchResponse(BaseModel):
    """Structured response containing search results and execution provenance."""

    query: str = Field(description="Exact user query submitted")
    results: list[SearchResultItem] = Field(
        default_factory=list,
        description="Ranked list of web search results",
    )
    total_results: int = Field(description="Total count of results returned")
    provider: str = Field(
        description="Search execution provider ('TAVILY_LIVE' or 'MOCK_SEARCH')",
    )
    is_live: bool = Field(
        description="True if query was executed live against the real Tavily Search API",
    )
    message: str | None = Field(
        default=None,
        description="Operational guidance or error details if search could not execute live",
    )

    model_config = ConfigDict(from_attributes=True)

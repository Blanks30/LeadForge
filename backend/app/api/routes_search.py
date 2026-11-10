"""API router for unrestricted general-purpose web search powered by Tavily."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.search_schema import SearchRequest, SearchResponse
from app.services.tavily_client import (
    TavilyAuthError,
    TavilyConfigError,
    TavilyError,
    TavilyNetworkError,
    TavilyRateLimitError,
    get_tavily_client,
)

router = APIRouter(prefix="/search", tags=["Web Search"])


@router.post("", response_model=SearchResponse)
async def perform_web_search(
    payload: SearchRequest,
) -> SearchResponse:
    """Execute general-purpose internet search via Tavily Search API.

    CRITICAL INVARIANTS:
    1. The query is passed verbatim without appending industry, SaaS, or geography keywords.
    2. Any natural-language topic can be searched.
    3. Searches do not automatically trigger TinyFish crawling or Gemini analysis.
    """
    client = get_tavily_client()
    try:
        return await client.search(
            query=payload.query,
            max_results=payload.max_results,
        )
    except TavilyConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except TavilyAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except TavilyRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except (TavilyNetworkError, TavilyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("", response_model=SearchResponse)
async def perform_web_search_get(
    q: Annotated[
        str,
        Query(
            min_length=1,
            max_length=500,
            description="General natural-language search query",
        ),
    ],
    max_results: Annotated[
        int,
        Query(ge=1, le=20, description="Maximum results to return"),
    ] = 8,
) -> SearchResponse:
    """GET variant for browser inspection and lightweight query invocation."""
    return await perform_web_search(SearchRequest(query=q, max_results=max_results))

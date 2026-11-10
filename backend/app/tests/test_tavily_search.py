"""Tests for Tavily general-purpose internet search integration."""

from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.tavily_client import TavilyClient


def test_search_endpoint_general_query_unrelated_to_saas():
    """Verify general-purpose internet search for topics completely unrelated to SaaS."""
    with TestClient(app) as client:
        # Non-SaaS query: AI agents
        res1 = client.post(
            "/api/search",
            json={"query": "Best open-source AI agents", "max_results": 5},
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["query"] == "Best open-source AI agents"
        assert len(data1["results"]) > 0
        assert data1["provider"] in ("TAVILY_LIVE", "MOCK_SEARCH")
        assert all(
            "url" in r and "title" in r and "content" in r for r in data1["results"]
        )

        # Non-SaaS query: Cybersecurity trends
        res2 = client.post(
            "/api/search",
            json={"query": "Cybersecurity trends and zero trust", "max_results": 3},
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["query"] == "Cybersecurity trends and zero trust"
        assert len(data2["results"]) > 0


def test_search_endpoint_company_queries():
    """Verify search for company-specific topics (e.g. Linways, Zoho competitors)."""
    with TestClient(app) as client:
        # Query for Linways
        res1 = client.post(
            "/api/search",
            json={"query": "Linways official website", "max_results": 4},
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert any("linways.com" in r.get("url", "") for r in data1["results"])

        # Query for Zoho competitors
        res2 = client.post(
            "/api/search",
            json={"query": "Competitors of Zoho", "max_results": 4},
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert len(data2["results"]) > 0


def test_search_preserves_exact_user_query_without_keyword_injection():
    """CRITICAL: Verify exact query is transmitted without appending SaaS or Indian keywords."""
    with TestClient(app) as client:
        raw_query = "latest developments in artificial intelligence"
        res = client.post("/api/search", json={"query": raw_query})
        assert res.status_code == 200
        data = res.json()
        # Query returned must strictly equal user input
        assert data["query"] == raw_query
        assert "SaaS" not in data["query"]
        assert "India" not in data["query"]


def test_search_get_variant():
    """Verify lightweight GET /api/search?q=... endpoint."""
    with TestClient(app) as client:
        res = client.get("/api/search?q=Cloud+computing+technologies")
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == "Cloud computing technologies"
        assert len(data["results"]) > 0


def test_search_rejects_empty_query():
    """Verify blank queries return 422 Unprocessable Entity."""
    with TestClient(app) as client:
        res1 = client.post("/api/search", json={"query": ""})
        assert res1.status_code == 422

        res2 = client.post("/api/search", json={"query": "   "})
        assert res2.status_code == 422


def test_missing_api_key_error_handling_in_live_mode():
    """Verify informative 503 error when running in live mode without TAVILY_API_KEY."""
    with (
        patch.object(settings, "USE_MOCK_APIS", False),
        patch.object(settings, "TAVILY_API_KEY", ""),
        TestClient(app) as client,
    ):
        res = client.post(
            "/api/search",
            json={"query": "Quantum computing algorithms"},
        )
        assert res.status_code == 503
        assert "TAVILY_API_KEY is not configured" in res.json()["detail"]


def test_live_search_payload_structure_and_verbatim_transmission():
    """Verify real Tavily client sends exact query in payload to https://api.tavily.com/search."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "query": "Machine learning architectures",
            "results": [
                {
                    "title": "Deep Learning Survey",
                    "url": "https://arxiv.org/abs/2101.00000",
                    "content": "A comprehensive survey of modern deep learning architectures.",
                    "score": 0.99,
                }
            ],
        },
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with (
        patch.object(settings, "USE_MOCK_APIS", False),
        patch.object(settings, "TAVILY_API_KEY", "tvly-test-key-mock"),
        patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post,
    ):
        mock_post.return_value = mock_response

        client = TavilyClient(api_key="tvly-test-key-mock")
        res = client._generate_mock_results("test", 1)  # smoke test
        assert res is not None

        # Call live search
        with TestClient(app) as test_client:
            response = test_client.post(
                "/api/search",
                json={"query": "Machine learning architectures", "max_results": 5},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["is_live"] is True
            assert data["provider"] == "TAVILY_LIVE"
            assert data["results"][0]["domain"] == "arxiv.org"

            # Assert exact payload sent to Tavily
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args.kwargs
            sent_payload = call_kwargs["json"]
            assert sent_payload["query"] == "Machine learning architectures"
            assert sent_payload["api_key"] == "tvly-test-key-mock"
            assert sent_payload["max_results"] == 5


def test_tavily_auth_error_handling():
    """Verify HTTP 401 when Tavily API key is invalid."""
    mock_response = httpx.Response(
        status_code=401,
        text="Unauthorized - invalid api key",
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with (
        patch.object(settings, "USE_MOCK_APIS", False),
        patch.object(settings, "TAVILY_API_KEY", "tvly-invalid-key"),
        patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post,
    ):
        mock_post.return_value = mock_response

        with TestClient(app) as test_client:
            response = test_client.post(
                "/api/search",
                json={"query": "Any query"},
            )
            assert response.status_code == 401
            assert "rejected authentication" in response.json()["detail"]


def test_tavily_rate_limit_error_handling():
    """Verify HTTP 429 when Tavily rate limit is exceeded."""
    mock_response = httpx.Response(
        status_code=429,
        text="Rate limit exceeded",
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with (
        patch.object(settings, "USE_MOCK_APIS", False),
        patch.object(settings, "TAVILY_API_KEY", "tvly-valid-key"),
        patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post,
    ):
        mock_post.return_value = mock_response

        with TestClient(app) as test_client:
            response = test_client.post(
                "/api/search",
                json={"query": "Any query"},
            )
            assert response.status_code == 429
            assert "rate limit exceeded" in response.json()["detail"]


def test_tavily_network_timeout_handling():
    """Verify HTTP 502 when network fails or times out."""
    with (
        patch.object(settings, "USE_MOCK_APIS", False),
        patch.object(settings, "TAVILY_API_KEY", "tvly-valid-key"),
        patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.ConnectTimeout("Connection timed out"),
        ),
        TestClient(app) as test_client,
    ):
        response = test_client.post(
            "/api/search",
            json={"query": "Any query"},
        )
        assert response.status_code == 502
        assert "Failed to connect to Tavily search service" in response.json()["detail"]

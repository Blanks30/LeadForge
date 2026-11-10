"""Tests for the API health check and route error handling."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok():
    """Verify health endpoint returns status ok, db true, and api_mode when database is accessible."""
    with TestClient(app) as client:
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"] is True
        assert data["api_mode"] in ("MOCK", "LIVE", "LIVE_VERIFIED", "LIVE_CONFIGURED")
        assert "live_connected" in data


def test_health_check_degraded_when_db_down():
    """Verify health endpoint returns degraded status if database connectivity fails."""
    with patch("app.main.check_db_health", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = False
        with TestClient(app) as client:
            response = client.get("/api/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["db"] is False
            assert data["api_mode"] in (
                "MOCK",
                "LIVE",
                "LIVE_VERIFIED",
                "LIVE_CONFIGURED",
            )


def test_unknown_route_returns_404():
    """Verify accessing an undefined API route returns standard 404 detail."""
    with TestClient(app) as client:
        response = client.get("/api/nonexistent")

        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}

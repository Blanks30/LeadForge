"""Tests for the API health check and route error handling."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok():
    """Verify health endpoint returns status ok and db true when database is accessible."""
    with TestClient(app) as client:
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "db": True}


def test_health_check_degraded_when_db_down():
    """Verify health endpoint returns degraded status if database connectivity fails."""
    with patch("app.main.check_db_health", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = False
        with TestClient(app) as client:
            response = client.get("/api/health")

            assert response.status_code == 200
            assert response.json() == {"status": "degraded", "db": False}


def test_unknown_route_returns_404():
    """Verify accessing an undefined API route returns standard 404 detail."""
    with TestClient(app) as client:
        response = client.get("/api/nonexistent")

        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}

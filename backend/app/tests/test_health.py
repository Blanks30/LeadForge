from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok():
    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_returns_404():
    client = TestClient(app)
    response = client.get("/api/nonexistent")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

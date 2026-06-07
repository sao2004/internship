"""Minimal smoke tests. CI runs these."""

from unittest.mock import patch

from fastapi.testclient import TestClient


def _client():
    from app.main import app
    return TestClient(app)


def test_health_endpoint_responds():
    with patch("app.main.r") as mock_redis:
        mock_redis.ping.return_value = True
        response = _client().get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_visits_increments():
    with patch("app.main.r") as mock_redis:
        mock_redis.incr.return_value = 42
        response = _client().get("/visits")
    assert response.status_code == 200
    assert response.json() == {"visits": 42}

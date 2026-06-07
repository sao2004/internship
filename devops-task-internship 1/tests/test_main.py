"""Smoke tests for all endpoints. CI runs these."""

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
    assert response.json()["redis"] is True


def test_health_redis_down():
    """Health should report redis=False when Redis is unreachable."""
    import redis as redis_lib
    with patch("app.main.r") as mock_redis:
        mock_redis.ping.side_effect = redis_lib.RedisError("down")
        response = _client().get("/health")
    assert response.status_code == 200
    assert response.json()["redis"] is False


def test_visits_increments():
    with patch("app.main.r") as mock_redis:
        mock_redis.incr.return_value = 42
        response = _client().get("/visits")
    assert response.status_code == 200
    assert response.json() == {"visits": 42}


def test_visits_count_no_increment():
    with patch("app.main.r") as mock_redis:
        mock_redis.get.return_value = "7"
        response = _client().get("/visits/count")
    assert response.status_code == 200
    assert response.json() == {"visits": 7}
    mock_redis.incr.assert_not_called()


def test_visits_count_empty_redis():
    """When key doesn't exist yet, should return 0."""
    with patch("app.main.r") as mock_redis:
        mock_redis.get.return_value = None
        response = _client().get("/visits/count")
    assert response.status_code == 200
    assert response.json() == {"visits": 0}


def test_visits_reset():
    with patch("app.main.r") as mock_redis:
        response = _client().post("/visits/reset")
    assert response.status_code == 200
    assert response.json() == {"visits": 0}
    mock_redis.set.assert_called_once_with("visits", 0)


def test_index_returns_html():
    with patch("app.main.r"):
        response = _client().get("/index")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Visit Counter" in response.text
    assert "visits/reset" in response.text

"""Tests for the Activity Tracker API.

Some of these tests currently FAIL. That is expected -
the failures point to the bugs you need to fix.

Run with: pytest -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage


@pytest.fixture(autouse=True)
def reset_storage():
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user(client):
    response = client.post(
        "/users", json={"email": "alice@example.com", "name": "Alice"}
    )
    assert response.status_code == 201
    return response.json()


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user_returns_payload(client):
    response = client.post("/users", json={"email": "bob@example.com", "name": "Bob"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "bob@example.com"
    assert body["name"] == "Bob"
    assert "id" in body


def test_get_user_by_id(client, user):
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == user["email"]


def test_get_user_missing_returns_404(client):
    response = client.get("/users/9999")
    assert response.status_code == 404


def test_create_event_returns_201(client, user):
    response = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "login", "metadata": {}},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["event_type"] == "login"
    assert body["user_id"] == user["id"]


def test_create_event_with_unknown_user_returns_404(client):
    response = client.post(
        "/events",
        json={"user_id": 9999, "event_type": "login", "metadata": {}},
    )
    assert response.status_code == 404


def test_list_events_includes_created_items(client, user):
    for event_type in ["login", "page_view", "click", "page_view", "logout"]:
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": event_type, "metadata": {}},
        )

    response = client.get("/events?offset=0&limit=10")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 5


def test_list_events_paginates_without_overlap(client, user):
    for i in range(10):
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {"i": i}},
        )

    page1 = client.get("/events?offset=0&limit=5").json()
    page2 = client.get("/events?offset=5&limit=5").json()

    assert len(page1) == 5
    assert len(page2) == 5
    page1_ids = {e["id"] for e in page1}
    page2_ids = {e["id"] for e in page2}
    assert page1_ids.isdisjoint(page2_ids), "Pages should not overlap"


def test_list_events_hides_soft_deleted_items(client, user):
    created_ids = []
    for _ in range(3):
        response = client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {}},
        )
        created_ids.append(response.json()["id"])

    delete_response = client.delete(f"/events/{created_ids[1]}")
    assert delete_response.status_code == 204

    response = client.get("/events?offset=0&limit=10")
    assert response.status_code == 200
    remaining_ids = {e["id"] for e in response.json()}
    assert created_ids[1] not in remaining_ids
    assert len(response.json()) == 2


def test_delete_missing_event_returns_404(client):
    response = client.delete("/events/9999")
    assert response.status_code == 404


def test_delete_same_event_twice_changes_response(client, user):
    create_response = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "click", "metadata": {}},
    )
    event_id = create_response.json()["id"]

    first_delete = client.delete(f"/events/{event_id}")
    second_delete = client.delete(f"/events/{event_id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 404

def test_list_user_events_returns_all_without_since(client, user):
    """Without a `since` filter, all non-deleted events for the user are returned."""
    for event_type in ["login", "page_view", "logout"]:
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": event_type, "metadata": {}},
        )

    response = client.get(f"/users/{user['id']}/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 3
    assert all(e["user_id"] == user["id"] for e in events)


def test_list_user_events_filters_by_since(client, user):
    """`since` filter excludes events created at or before the given timestamp."""
    from datetime import datetime, timezone, timedelta

    # Create two events before the cutoff
    for _ in range(2):
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {}},
        )

    # Record cutoff *after* those events exist
    cutoff = datetime.now(timezone.utc)

    # Create two events that should appear in the filtered results
    for _ in range(2):
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "purchase", "metadata": {}},
        )

    response = client.get(
        f"/users/{user['id']}/events",
        params={"since": cutoff.isoformat()},
    )
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert all(e["event_type"] == "purchase" for e in events)


def test_list_user_events_unknown_user_returns_404(client):
    """`GET /users/{user_id}/events` returns 404 for a non-existent user."""
    response = client.get("/users/9999/events")
    assert response.status_code == 404


def test_list_user_events_excludes_soft_deleted(client, user):
    """Soft-deleted events are not included in the user event list."""
    ids = []
    for _ in range(3):
        r = client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "login", "metadata": {}},
        )
        ids.append(r.json()["id"])

    client.delete(f"/events/{ids[0]}")

    response = client.get(f"/users/{user['id']}/events")
    assert response.status_code == 200
    returned_ids = {e["id"] for e in response.json()}
    assert ids[0] not in returned_ids
    assert len(returned_ids) == 2


def test_list_user_events_only_returns_own_events(client, client_fixture=None):
    """Events from other users are not included."""
    from fastapi.testclient import TestClient
    from app.main import app

    c = TestClient(app)
    alice = c.post("/users", json={"email": "a@x.com", "name": "Alice"}).json()
    bob = c.post("/users", json={"email": "b@x.com", "name": "Bob"}).json()

    c.post("/events", json={"user_id": alice["id"], "event_type": "login", "metadata": {}})
    c.post("/events", json={"user_id": bob["id"], "event_type": "login", "metadata": {}})
    c.post("/events", json={"user_id": alice["id"], "event_type": "logout", "metadata": {}})

    response = c.get(f"/users/{alice['id']}/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert all(e["user_id"] == alice["id"] for e in events)


def test_pagination_after_delete_stays_consistent(client, user):
    created_ids = []
    for i in range(6):
        response = client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {"i": i}},
        )
        created_ids.append(response.json()["id"])

    delete_response = client.delete(f"/events/{created_ids[2]}")
    assert delete_response.status_code == 204

    page1 = client.get("/events?offset=0&limit=3")
    page2 = client.get("/events?offset=3&limit=3")

    assert page1.status_code == 200
    assert page2.status_code == 200

    page1_ids = [event["id"] for event in page1.json()]
    page2_ids = [event["id"] for event in page2.json()]

    assert created_ids[2] not in page1_ids + page2_ids
    assert len(page1_ids) == 3
    assert len(page2_ids) == 2
    assert set(page1_ids).isdisjoint(page2_ids), "Pages should not overlap"

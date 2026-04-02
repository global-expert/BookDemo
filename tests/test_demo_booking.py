from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def test_book_demo_creates_booking() -> None:
    from tests.conftest import get_test_client

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Mariam Noor",
        "email": "mariam@example.com",
        "industry": "Technology",
        "meeting_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }

    response = client.post("/api/v1/demo/book", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Demo booked successfully. We will contact you shortly to confirm your demo."
    assert body["status"] == "pending"
    assert body["email"] == "mariam@example.com"


def test_book_demo_rejects_past_time() -> None:
    from tests.conftest import get_test_client

    client: TestClient = get_test_client()
    payload = {
        "full_name": "Mariam Noor",
        "email": "mariam@example.com",
        "industry": "Technology",
        "meeting_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }

    response = client.post("/api/v1/demo/book", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Meeting time must be in the future"
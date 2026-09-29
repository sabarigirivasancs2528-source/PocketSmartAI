import os


os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_pocketsmart.db"

os.environ[
    "SECRET_KEY"
] = "test-secret"

os.environ[
    "GEMINI_API_KEY"
] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_register_login_home():

    email = "test@example.com"

    response = client.post(
        "/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "password123"
        }
    )

    assert response.status_code in (
        201,
        409
    )

    login = client.post(
        "/login",
        data={
            "email": email,
            "password": "password123"
        }
    )

    assert login.status_code == 200

    response = client.post(
        "/generate-home",
        json={
            "budget": 100000,
            "rooms": [
                "Living Room"
            ],
            "items": {
                "sofa": 1
            },
            "style": "modern",
            "priorities": "value"
        }
    )

    assert response.status_code == 200

    assert (
        response.json()
        ["result"]
        ["recommendations"]
    )
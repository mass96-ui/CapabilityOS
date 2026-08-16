from __future__ import annotations

from fastapi.testclient import TestClient


def test_rate_limit_blocks_excessive_requests(client: TestClient) -> None:
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPass1!",
            },
        )

        assert response.status_code in (401, 422, 429)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass1!",
        },
    )

    assert response.status_code == 429
    assert "Too many requests" in response.json()["error"]["message"]


def test_rate_limit_allows_normal_usage(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPass1!",
            },
        )

        assert response.status_code in (401, 422)

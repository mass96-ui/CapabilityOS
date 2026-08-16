from __future__ import annotations

import app.api.v1.auth as auth_module

from fastapi.testclient import TestClient


def _message(response) -> str:
    data = response.json()
    return (
        data.get("error", {}).get("message")
        or data.get("detail", "")
    )


def test_registration_rejects_weak_password(client: TestClient) -> None:
    weak_passwords = [
        "short",
        "alllowercase1!",
        "ALLUPPERCASE1!",
        "NoSpecial1",
        "NoNumber!",
    ]

    for password in weak_passwords:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Test",
                "last_name": "Learner",
                "username": f"user_{hash(password)}",
                "email": f"test_{hash(password)}@example.com",
                "password": password,
                "confirm_password": password,
            },
        )

        assert response.status_code == 422, (
            f"Expected 422 for password: {password}"
        )


def test_registration_accepts_strong_password(client: TestClient, monkeypatch) -> None:
    captured: dict[str, str] = {}

    async def fake_send_verification_email(
        email: str,
        first_name: str,
        otp: str,
    ) -> None:
        captured["email"] = email

    monkeypatch.setattr(
        auth_module,
        "_send_verification_email",
        fake_send_verification_email,
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test",
            "last_name": "Learner",
            "username": "strongpassuser",
            "email": "strongpass@example.com",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
        },
    )

    assert response.status_code == 201, response.text

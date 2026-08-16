from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.database.session import AsyncSessionFactory
from app.models.user import User
from app.services.email import EmailService


def test_password_reset_flow(client: TestClient) -> None:
    async def seed():
        async with AsyncSessionFactory() as session:
            user = User(
                first_name="Reset",
                last_name="Test",
                username="reset_test_user",
                email="reset@test.example.com",
                password_hash="old-hash",
            )
            session.add(user)
            await session.flush()
            return user.id

    user_id = asyncio.run(seed())

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset@test.example.com"},
    )

    if response.status_code != 202:
        print(f"Response: {response.status_code} {response.text}")

    assert response.status_code == 202

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@test.example.com"},
    )

    assert response.status_code == 202


def test_password_reset_with_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid-token",
            "password": "NewPass1!",
            "confirm_password": "NewPass1!",
        },
    )

    assert response.status_code == 400
    assert "Invalid or expired" in response.json()["error"]["message"]


def test_password_reset_url_uses_configured_frontend() -> None:
    async def seed():
        async with AsyncSessionFactory() as session:
            user = User(
                first_name="URL",
                last_name="Test",
                username="url_test_user",
                email="url@test.example.com",
                password_hash="old-hash",
            )
            session.add(user)
            await session.flush()
            await session.commit()
            return user.id

    async def run_test():
        with patch(
            "app.services.email.EmailService._send_raw",
            new_callable=AsyncMock,
        ):
            async with AsyncSessionFactory() as session:
                from app.services.password_reset import PasswordResetService

                service = PasswordResetService(session)
                await service.request_reset(email="url@test.example.com")

                email_call = EmailService._send_raw.call_args
                assert email_call is not None
                email_body = email_call.kwargs["body"]
                expected_url = f"{settings.FRONTEND_URL}/reset-password?token="
                assert expected_url in email_body

    user_id = asyncio.run(seed())

    custom_frontend = "https://app.example.com"
    original_frontend = settings.FRONTEND_URL

    try:
        settings.FRONTEND_URL = custom_frontend
        asyncio.run(run_test())
    finally:
        settings.FRONTEND_URL = original_frontend

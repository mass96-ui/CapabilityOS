from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.database.session import AsyncSessionFactory
from app.models.user import User
from app.services.passport import EngineeringPassportService


def _user(
    user_id: str = "passport-user-id",
    email: str = "passport@test.local",
    username: str = "passport_user",
) -> User:
    return User(
        id=user_id,
        first_name="Passport",
        last_name="Test",
        username=username,
        email=email,
        password_hash="test-hash",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        role="learner",
    )


def test_passport_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/learner/passport")

    assert response.status_code == 401


def test_passport_returns_authenticated_learner_data(
    client: TestClient,
) -> None:
    user = _user()

    async def persist_user() -> None:
        async with AsyncSessionFactory() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

    asyncio.run(persist_user())

    from app.core.dependencies import get_current_user
    from app.main import app

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get("/api/v1/learner/passport")

        assert response.status_code == 200

        data = response.json()

        assert data["profile"]["id"] == user.id
        assert data["profile"]["email"] == user.email
        assert data["profile"]["username"] == user.username
        assert "capabilities" in data
        assert "assessment_history" in data
        assert "capability_history" in data
        assert "project_experience" in data
        assert "generated_at" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_passport_service_builds_empty_passport_for_new_learner() -> None:
    user = User(
        id="empty-passport-user",
        first_name="Empty",
        last_name="Passport",
        username="empty_passport",
        email="empty@test.local",
        password_hash="test-hash",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        role="learner",
    )

    async with AsyncSessionFactory() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = EngineeringPassportService(session)
        passport = await service.build_passport(user_id=user.id)

        assert passport.profile.id == user.id
        assert passport.capabilities == []
        assert passport.assessment_history == []
        assert passport.capability_history == []
        assert passport.project_experience == []
        assert passport.generated_at is not None

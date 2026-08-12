import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.database.session import AsyncSessionFactory
from app.main import app
from app.models.capability import Capability
from app.models.project import Project
from app.models.project_requirement import ProjectRequirement
from app.models.user import User
from app.models.user_capability import UserCapability


def test_project_matching_api():
    async def seed():
        async with AsyncSessionFactory() as session:
            suffix = uuid.uuid4().hex[:8]

            user = User(
                first_name="API",
                last_name="Match",
                username=f"api_match_{suffix}",
                email=f"api.match.{suffix}@test.local",
                password_hash="test-password-hash",
            )

            capability = Capability(
                name=f"Python API {suffix}",
                slug=f"python-api-{suffix}",
                category="technical",
            )

            session.add_all([user, capability])
            await session.flush()

            project = Project(
                name=f"Matching API Project {suffix}",
                description="API integration test",
                status="open",
                project_type="practical",
                owner_id=user.id,
            )

            requirement = ProjectRequirement(
                project_id=project.id,
                capability_id=capability.id,
                minimum_proficiency_level=3,
                importance=1.0,
                required=True,
            )

            user_capability = UserCapability(
                user_id=user.id,
                capability_id=capability.id,
                proficiency_level=4,
                score=90.0,
                confidence=0.95,
                verified=True,
            )

            session.add(project)
            await session.flush()

            requirement.project_id = project.id

            session.add_all(
                [requirement, user_capability]
            )
            await session.flush()

            return user.id, project.id

    import asyncio

    user_id, project_id = asyncio.run(seed())
async def get_test_user():
    return User(id=user_id)


    app.dependency_overrides[get_current_user] = get_test_user

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/projects/{project_id}/match"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["project_id"] == project_id
        assert data["user_id"] == user_id
        assert data["eligible"] is True
        assert data["match_score"] == 100.0
        assert len(data["matched"]) == 1
        assert data["gaps"] == []
        assert data["missing"] == []

    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )



from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import AsyncSessionFactory
from app.main import app
from app.models.capability import Capability
from app.models.project import Project
from app.models.project_requirement import ProjectRequirement
from app.models.user import User
from app.models.user_capability import UserCapability


def _seed_project_marketplace():
    async def seed():
        async with AsyncSessionFactory() as session:
            suffix = uuid.uuid4().hex[:8]

            manager = User(
                first_name="Manager",
                last_name="One",
                username=f"manager_{suffix}",
                email=f"manager.{suffix}@test.local",
                password_hash="test-password-hash",
                role="manager",
            )

            other_manager = User(
                first_name="Manager",
                last_name="Two",
                username=f"manager2_{suffix}",
                email=f"manager2.{suffix}@test.local",
                password_hash="test-password-hash",
                role="manager",
            )

            learner = User(
                first_name="Learner",
                last_name="One",
                username=f"learner_{suffix}",
                email=f"learner.{suffix}@test.local",
                password_hash="test-password-hash",
                role="learner",
            )

            capability = Capability(
                name=f"Python {suffix}",
                slug=f"python-{suffix}",
                category="technical",
            )

            second_capability = Capability(
                name=f"TypeScript {suffix}",
                slug=f"typescript-{suffix}",
                category="technical",
            )

            session.add_all([manager, other_manager, learner, capability, second_capability])
            await session.flush()

            project = Project(
                name=f"Test Project {suffix}",
                description="Test",
                status="open",
                project_type="real_world",
                owner_id=manager.id,
            )

            other_project = Project(
                name=f"Other Project {suffix}",
                description="Test",
                status="open",
                project_type="real_world",
                owner_id=other_manager.id,
            )

            session.add_all([project, other_project])
            await session.flush()

            requirement = ProjectRequirement(
                project_id=project.id,
                capability_id=capability.id,
                minimum_proficiency_level=3,
                importance=1.0,
                required=True,
            )

            other_requirement = ProjectRequirement(
                project_id=other_project.id,
                capability_id=capability.id,
                minimum_proficiency_level=3,
                importance=1.0,
                required=True,
            )

            session.add_all([requirement, other_requirement])
            await session.flush()

            user_capability = UserCapability(
                user_id=learner.id,
                capability_id=capability.id,
                proficiency_level=4,
                score=90.0,
                confidence=0.95,
                verified=True,
            )

            session.add(user_capability)
            await session.commit()

            return {
                "manager_id": manager.id,
                "other_manager_id": other_manager.id,
                "learner_id": learner.id,
                "project_id": project.id,
                "other_project_id": other_project.id,
                "requirement_id": requirement.id,
                "other_requirement_id": other_requirement.id,
                "capability_id": capability.id,
                "second_capability_id": second_capability.id,
            }

    import asyncio
    return asyncio.run(seed())


def _override_user(user_id: str, role: str = "learner"):
    async def get_test_user():
        return User(id=user_id, role=role)

    app.dependency_overrides[get_current_user] = get_test_user


def _clear_override():
    app.dependency_overrides.pop(get_current_user, None)


class TestLearnerProjectAuthorization:
    def test_learner_cannot_create_project(self):
        data = _seed_project_marketplace()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/projects",
                    json={
                        "name": "Learner Project",
                        "description": "Test",
                        "project_type": "real_world",
                        "owner_id": data["learner_id"],
                    },
                )
            assert response.status_code == 403
        finally:
            _clear_override()

    def test_learner_cannot_update_another_users_project(self):
        data = _seed_project_marketplace()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.patch(
                    f"/api/v1/projects/{data['project_id']}",
                    json={"name": "Hacked"},
                )
            assert response.status_code == 403
        finally:
            _clear_override()

    def test_learner_cannot_delete_another_users_project(self):
        data = _seed_project_marketplace()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.delete(
                    f"/api/v1/projects/{data['project_id']}"
                )
            assert response.status_code == 403
        finally:
            _clear_override()


class TestManagerProjectAuthorization:
    def test_manager_can_create_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/projects",
                    json={
                        "name": "Manager Project",
                        "description": "Test",
                        "project_type": "real_world",
                        "owner_id": data["manager_id"],
                    },
                )
            assert response.status_code == 201
            assert response.json()["name"] == "Manager Project"
        finally:
            _clear_override()

    def test_manager_can_update_own_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.patch(
                    f"/api/v1/projects/{data['project_id']}",
                    json={"name": "Updated Name"},
                )
            assert response.status_code == 200
            assert response.json()["name"] == "Updated Name"
        finally:
            _clear_override()

    def test_manager_cannot_update_another_managers_project(self):
        data = _seed_project_marketplace()
        _override_user(data["other_manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.patch(
                    f"/api/v1/projects/{data['project_id']}",
                    json={"name": "Hacked"},
                )
            assert response.status_code == 403
        finally:
            _clear_override()

    def test_manager_can_delete_own_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.delete(
                    f"/api/v1/projects/{data['project_id']}"
                )
            assert response.status_code == 200
        finally:
            _clear_override()


class TestManagerRequirementAuthorization:
    def test_manager_can_create_requirement_for_own_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.post(
                    f"/api/v1/projects/{data['project_id']}/requirements",
                    json={
                        "project_id": data["project_id"],
                        "capability_id": data["second_capability_id"],
                        "minimum_proficiency_level": 3,
                        "importance": 1.0,
                        "required": True,
                    },
                )
            assert response.status_code == 201
        finally:
            _clear_override()

    def test_manager_cannot_create_requirement_for_another_managers_project(self):
        data = _seed_project_marketplace()
        _override_user(data["other_manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.post(
                    f"/api/v1/projects/{data['project_id']}/requirements",
                    json={
                        "project_id": data["project_id"],
                        "capability_id": data["capability_id"],
                        "minimum_proficiency_level": 3,
                        "importance": 1.0,
                        "required": True,
                    },
                )
            assert response.status_code == 403
        finally:
            _clear_override()

    def test_manager_can_update_requirement_for_own_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.patch(
                    f"/api/v1/projects/requirements/{data['requirement_id']}",
                    json={"required": False},
                )
            assert response.status_code == 200
            assert response.json()["required"] is False
        finally:
            _clear_override()

    def test_manager_cannot_update_requirement_for_another_managers_project(self):
        data = _seed_project_marketplace()
        _override_user(data["other_manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.patch(
                    f"/api/v1/projects/requirements/{data['requirement_id']}",
                    json={"required": False},
                )
            assert response.status_code == 403
        finally:
            _clear_override()

    def test_manager_can_delete_requirement_for_own_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.delete(
                    f"/api/v1/projects/requirements/{data['requirement_id']}"
                )
            assert response.status_code == 200
        finally:
            _clear_override()

    def test_manager_cannot_delete_requirement_for_another_managers_project(self):
        data = _seed_project_marketplace()
        _override_user(data["other_manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.delete(
                    f"/api/v1/projects/requirements/{data['requirement_id']}"
                )
            assert response.status_code == 403
        finally:
            _clear_override()


class TestManagerMatchingAuthorization:
    def test_learner_cannot_view_manager_matches(self):
        data = _seed_project_marketplace()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/matches"
                )
            assert response.status_code == 403
        finally:
            _clear_override()

    def test_manager_can_view_matches_for_own_project(self):
        data = _seed_project_marketplace()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/matches"
                )
            assert response.status_code == 200
            body = response.json()
            assert body["project_id"] == data["project_id"]
            assert "matches" in body
        finally:
            _clear_override()

    def test_manager_cannot_view_matches_for_another_managers_project(self):
        data = _seed_project_marketplace()
        _override_user(data["other_manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/matches"
                )
            assert response.status_code == 403
        finally:
            _clear_override()

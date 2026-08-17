from __future__ import annotations

import uuid

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


def _seed_capability_name_data():
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

            session.add_all([manager, learner, capability, second_capability])
            await session.flush()

            project = Project(
                name=f"Test Project {suffix}",
                description="Test",
                status="open",
                project_type="real_world",
                owner_id=manager.id,
            )

            session.add(project)
            await session.flush()

            requirement = ProjectRequirement(
                project_id=project.id,
                capability_id=capability.id,
                minimum_proficiency_level=3,
                importance=1.0,
                required=True,
            )

            other_requirement = ProjectRequirement(
                project_id=project.id,
                capability_id=second_capability.id,
                minimum_proficiency_level=2,
                importance=0.8,
                required=False,
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
                "learner_id": learner.id,
                "project_id": project.id,
                "requirement_id": requirement.id,
                "other_requirement_id": other_requirement.id,
                "capability_id": capability.id,
                "capability_name": capability.name,
                "second_capability_id": second_capability.id,
                "second_capability_name": second_capability.name,
            }

    import asyncio
    return asyncio.run(seed())


def _override_user(user_id: str, role: str = "learner"):
    async def get_test_user():
        return User(id=user_id, role=role)

    app.dependency_overrides[get_current_user] = get_test_user


def _clear_override():
    app.dependency_overrides.pop(get_current_user, None)


class TestCapabilityNameResolution:
    def test_learner_match_includes_capability_names(self):
        data = _seed_capability_name_data()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/match"
                )
            assert response.status_code == 200
            body = response.json()
            assert body["eligible"] is True
            matched_capability_names = [
                m["capability_name"] for m in body["matched"]
            ]
            assert data["capability_name"] in matched_capability_names
            missing_capability_names = [
                m["capability_name"] for m in body["missing"]
            ]
            assert data["second_capability_name"] in missing_capability_names
        finally:
            _clear_override()

    def test_manager_matches_include_capability_names(self):
        data = _seed_capability_name_data()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/matches"
                )
            assert response.status_code == 200
            body = response.json()
            assert body["total_candidates"] >= 1
            candidate = next(
                (c for c in body["matches"] if c["user_id"] == data["learner_id"]),
                None,
            )
            assert candidate is not None
            matched_names = [m["capability_name"] for m in candidate["matched"]]
            assert data["capability_name"] in matched_names
            missing_names = [m["capability_name"] for m in candidate["missing"]]
            assert data["second_capability_name"] in missing_names
        finally:
            _clear_override()

    def test_match_response_includes_coverage_ratio(self):
        data = _seed_capability_name_data()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/match"
                )
            assert response.status_code == 200
            body = response.json()
            assert "coverage_ratio" in body
            assert body["coverage_ratio"] == 0.5
        finally:
            _clear_override()


class TestManagerMatchesPagination:
    def test_manager_matches_pagination(self):
        data = _seed_capability_name_data()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/matches",
                    params={"page": 1, "page_size": 10},
                )
            assert response.status_code == 200
            body = response.json()
            assert body["page"] == 1
            assert body["page_size"] == 10
            assert "total_pages" in body
            assert "total_candidates" in body
            assert "eligible_count" in body
        finally:
            _clear_override()

    def test_manager_matches_empty_page(self):
        data = _seed_capability_name_data()
        _override_user(data["manager_id"], role="manager")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/matches",
                    params={"page": 5, "page_size": 10},
                )
            assert response.status_code == 200
            body = response.json()
            assert body["matches"] == []
        finally:
            _clear_override()


class TestProjectRequirementResponseNames:
    def test_get_project_requirements_includes_capability_name(self):
        data = _seed_capability_name_data()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{data['project_id']}/requirements"
                )
            assert response.status_code == 200
            body = response.json()
            assert len(body) >= 1
            for req in body:
                assert "capability_name" in req
        finally:
            _clear_override()


class TestProjectSearchFilter:
    def test_get_projects_supports_search(self):
        data = _seed_capability_name_data()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.get(
                    "/api/v1/projects",
                    params={"q": data["project_id"]},
                )
            assert response.status_code == 200
            body = response.json()
            assert isinstance(body, list)
        finally:
            _clear_override()

    def test_get_projects_supports_status_filter(self):
        data = _seed_capability_name_data()
        _override_user(data["learner_id"], role="learner")
        try:
            with TestClient(app) as client:
                response = client.get(
                    "/api/v1/projects",
                    params={"status": "open"},
                )
            assert response.status_code == 200
            body = response.json()
            assert isinstance(body, list)
        finally:
            _clear_override()

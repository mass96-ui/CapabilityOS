from __future__ import annotations

import pytest

from app.models.project import Project
from app.models.user import User
from app.services.project import ProjectService


def _project(owner_id: str) -> Project:
    return Project(
        id="project-id",
        name="Test Project",
        description="Test",
        status="draft",
        project_type="real_world",
        owner_id=owner_id,
    )


def _user(user_id: str, role: str = "learner", is_superuser: bool = False) -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username="testuser",
        email="test@example.com",
        password_hash="test-hash",
        is_active=True,
        is_verified=True,
        is_superuser=is_superuser,
        role=role,
    )


def test_owner_can_modify_project():
    owner = _user("owner-id", role="learner")
    project = _project(owner_id=owner.id)

    service = ProjectService(
        session=None,
        current_user=owner,
    )

    service._require_owner_or_admin(project)


def test_non_owner_cannot_modify_project():
    owner = _user("owner-id", role="learner")
    other = _user("other-id", role="learner")
    project = _project(owner_id=owner.id)

    service = ProjectService(
        session=None,
        current_user=other,
    )

    with pytest.raises(ValueError) as exc_info:
        service._require_owner_or_admin(project)

    assert "permission" in str(exc_info.value).lower()


def test_admin_can_modify_any_project():
    admin = _user("admin-id", role="admin", is_superuser=True)
    owner = _user("owner-id", role="learner")
    project = _project(owner_id=owner.id)

    service = ProjectService(
        session=None,
        current_user=admin,
    )

    service._require_owner_or_admin(project)


def test_superuser_can_modify_any_project():
    superuser = _user("superuser-id", role="learner", is_superuser=True)
    owner = _user("owner-id", role="learner")
    project = _project(owner_id=owner.id)

    service = ProjectService(
        session=None,
        current_user=superuser,
    )

    service._require_owner_or_admin(project)

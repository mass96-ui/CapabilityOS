from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.dependencies import _RoleRequired
from app.models.user import User


def _user(role: str = "learner", is_superuser: bool = False) -> User:
    return User(
        id="test-user-id",
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


def test_admin_dependency_accepts_admin():
    user = _user(role="admin")
    result = _RoleRequired({"admin"})(user)
    assert result.id == "test-user-id"


def test_admin_dependency_accepts_superuser():
    user = _user(role="learner", is_superuser=True)
    result = _RoleRequired({"admin"})(user)
    assert result.id == "test-user-id"


def test_admin_dependency_rejects_manager():
    user = _user(role="manager")

    with pytest.raises(HTTPException) as exc_info:
        _RoleRequired({"admin"})(user)

    assert exc_info.value.status_code == 403


def test_admin_dependency_rejects_learner():
    user = _user(role="learner")

    with pytest.raises(HTTPException) as exc_info:
        _RoleRequired({"admin"})(user)

    assert exc_info.value.status_code == 403


def test_manager_dependency_accepts_admin():
    user = _user(role="admin")
    result = _RoleRequired({"admin", "manager"})(user)
    assert result.id == "test-user-id"


def test_manager_dependency_accepts_manager():
    user = _user(role="manager")
    result = _RoleRequired({"admin", "manager"})(user)
    assert result.id == "test-user-id"


def test_manager_dependency_accepts_superuser():
    user = _user(role="learner", is_superuser=True)
    result = _RoleRequired({"admin", "manager"})(user)
    assert result.id == "test-user-id"


def test_manager_dependency_rejects_learner():
    user = _user(role="learner")

    with pytest.raises(HTTPException) as exc_info:
        _RoleRequired({"admin", "manager"})(user)

    assert exc_info.value.status_code == 403


def test_learner_dependency_accepts_learner():
    user = _user(role="learner")
    result = _RoleRequired({"admin", "manager", "learner"})(user)
    assert result.id == "test-user-id"


def test_learner_dependency_accepts_admin():
    user = _user(role="admin")
    result = _RoleRequired({"admin", "manager", "learner"})(user)
    assert result.id == "test-user-id"


def test_learner_dependency_accepts_manager():
    user = _user(role="manager")
    result = _RoleRequired({"admin", "manager", "learner"})(user)
    assert result.id == "test-user-id"

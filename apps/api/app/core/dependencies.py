from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.database.session import get_session
from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.jwt import JWTManager


# ============================================================
# Application Settings Dependency
# ============================================================

def get_app_settings() -> Settings:
    """
    Returns the singleton application settings.
    """
    return settings


# ============================================================
# Database Session Dependency
# ============================================================

async def get_db() -> AsyncSession:
    """
    Provides a database session for each request.
    """
    async for session in get_session():
        yield session


# ============================================================
# Authentication Security Scheme
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=False,
)


# ============================================================
# Current Authenticated User
# ============================================================

async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Resolve the currently authenticated user from
    the Bearer JWT access token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # --------------------------------------------------------
    # Check token exists
    # --------------------------------------------------------

    if not token:
        raise credentials_exception

    # --------------------------------------------------------
    # Verify JWT
    # --------------------------------------------------------

    try:
        payload = JWTManager.verify_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user_repo = UserRepository(db)

    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    # --------------------------------------------------------
    # Check account status
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ============================================================
# Role-Based Authorization
# ============================================================

def _RoleRequired(allowed_roles: set[str]):
    """
    Reusable authorization dependency factory.

    Supports the unified User model role system:

    - learner (default)
    - manager
    - admin

    ``is_superuser`` is preserved for backward compatibility
    and grants full platform administration access.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        is_admin = current_user.is_superuser or current_user.role == "admin"
        is_manager = is_admin or current_user.role == "manager"

        if "admin" in allowed_roles and is_admin:
            return current_user

        if "manager" in allowed_roles and is_manager:
            return current_user

        if "learner" in allowed_roles:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )

    return dependency


AdminDep = Annotated[
    User,
    Depends(_RoleRequired({"admin"})),
]

ManagerDep = Annotated[
    User,
    Depends(_RoleRequired({"admin", "manager"})),
]

LearnerDep = Annotated[
    User,
    Depends(_RoleRequired({"admin", "manager", "learner"})),
]


# ============================================================
# Typed Dependency Aliases
# ============================================================

SettingsDep = Annotated[
    Settings,
    Depends(get_app_settings),
]

DatabaseDep = Annotated[
    AsyncSession,
    Depends(get_db),
]

CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]

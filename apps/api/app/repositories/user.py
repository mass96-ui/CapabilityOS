from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for all User database operations.

    This repository extends the generic BaseRepository
    with user-specific queries.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=User)

    # ==========================================================
    # GET BY EMAIL
    # ==========================================================

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    # ==========================================================
    # GET BY USERNAME
    # ==========================================================

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    # ==========================================================
    # CHECK EMAIL EXISTS
    # ==========================================================

    async def email_exists(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    # ==========================================================
    # CHECK USERNAME EXISTS
    # ==========================================================

    async def username_exists(self, username: str) -> bool:
        return await self.get_by_username(username) is not None

    # ==========================================================
    # LOGIN LOOKUP
    # ==========================================================

    async def get_by_login(self, login: str) -> User | None:
        """
        Accept either email or username.
        """
        statement = select(User).where(
            or_(
                User.email == login,
                User.username == login,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    # ==========================================================
    # ACTIVE USERS
    # ==========================================================

    async def get_active_users(self) -> list[User]:
        statement = select(User).where(User.is_active.is_(True))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    # ==========================================================
    # VERIFIED USERS
    # ==========================================================

    async def get_verified_users(self) -> list[User]:
        statement = select(User).where(User.is_verified.is_(True))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    # ==========================================================
    # SUPER USERS
    # ==========================================================

    async def get_superusers(self) -> list[User]:
        statement = select(User).where(User.is_superuser.is_(True))
        result = await self.session.execute(statement)
        return list(result.scalars().all())
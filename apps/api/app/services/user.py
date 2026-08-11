from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.base import BaseService


class UserService(BaseService[User]):
    """
    User business logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Fetch a user by email.
        """
        statement = select(User).where(User.email == email)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check whether an email already exists.
        """
        user = await self.get_by_email(email)
        return user is not None

    async def username_exists(self, username: str) -> bool:
        """
        Check whether a username already exists.
        """
        statement = select(User).where(User.username == username)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none() is not None
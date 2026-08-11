from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learner.profile import LearnerProfile
from app.repositories.base import BaseRepository


class LearnerProfileRepository(BaseRepository[LearnerProfile]):
    """
    Repository for learner profile persistence.

    Database access only.
    Business rules remain inside the service layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=LearnerProfile,
        )

    # ==========================================================
    # GET BY USER
    # ==========================================================

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> LearnerProfile | None:
        statement = select(LearnerProfile).where(
            LearnerProfile.user_id == user_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    # ==========================================================
    # CHECK PROFILE EXISTS
    # ==========================================================

    async def exists_for_user(
        self,
        user_id: str,
    ) -> bool:
        return await self.get_by_user_id(user_id) is not None
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_attempt import AssessmentAttempt
from app.repositories.base import BaseRepository


class AssessmentAttemptRepository(
    BaseRepository[AssessmentAttempt]
):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model=AssessmentAttempt,
        )

    async def get_by_user_and_assessment(
        self,
        user_id: str,
        assessment_id: str,
    ) -> list[AssessmentAttempt]:
        result = await self.session.execute(
            select(AssessmentAttempt)
            .where(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.assessment_id == assessment_id,
            )
            .order_by(
                AssessmentAttempt.created_at.desc()
            )
        )

        return list(result.scalars().all())

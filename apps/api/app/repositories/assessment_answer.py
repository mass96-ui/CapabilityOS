from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_answer import AssessmentAnswer
from app.repositories.base import BaseRepository


class AssessmentAnswerRepository(
    BaseRepository[AssessmentAnswer]
):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model=AssessmentAnswer,
        )

    async def get_by_attempt(
        self,
        attempt_id: str,
    ) -> list[AssessmentAnswer]:
        result = await self.session.execute(
            select(AssessmentAnswer)
            .where(
                AssessmentAnswer.attempt_id == attempt_id
            )
            .order_by(
                AssessmentAnswer.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def get_by_attempt_and_question(
        self,
        attempt_id: str,
        question_id: str,
    ) -> AssessmentAnswer | None:
        result = await self.session.execute(
            select(AssessmentAnswer).where(
                AssessmentAnswer.attempt_id == attempt_id,
                AssessmentAnswer.question_id == question_id,
            )
        )

        return result.scalar_one_or_none()

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_question import AssessmentQuestion
from app.repositories.base import BaseRepository


class AssessmentQuestionRepository(
    BaseRepository[AssessmentQuestion]
):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model=AssessmentQuestion,
        )

    async def get_by_assessment(
        self,
        assessment_id: str,
        active_only: bool = True,
    ) -> list[AssessmentQuestion]:
        query = (
            select(AssessmentQuestion)
            .where(
                AssessmentQuestion.assessment_id
                == assessment_id
            )
            .order_by(
                AssessmentQuestion.question_order.asc()
            )
        )

        if active_only:
            query = query.where(
                AssessmentQuestion.is_active.is_(True)
            )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_by_assessment_and_order(
        self,
        assessment_id: str,
        question_order: int,
    ) -> AssessmentQuestion | None:
        result = await self.session.execute(
            select(AssessmentQuestion).where(
                AssessmentQuestion.assessment_id
                == assessment_id,
                AssessmentQuestion.question_order
                == question_order,
            )
        )

        return result.scalar_one_or_none()

    async def count_by_assessment(
        self,
        assessment_id: str,
        active_only: bool = True,
    ) -> int:
        query = select(
            func.count(AssessmentQuestion.id)
        ).where(
            AssessmentQuestion.assessment_id
            == assessment_id
        )

        if active_only:
            query = query.where(
                AssessmentQuestion.is_active.is_(True)
            )

        result = await self.session.execute(query)

        return int(result.scalar_one())

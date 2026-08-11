from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.assessment import AssessmentRepository
from app.repositories.assessment_question import (
    AssessmentQuestionRepository,
)


class AssessmentQuestionService:
    def __init__(self, session: AsyncSession):
        self.repository = AssessmentQuestionRepository(session)
        self.assessment_repository = AssessmentRepository(session)

    async def get_question(
        self,
        question_id: str,
    ):
        return await self.repository.get_by_id(
            question_id
        )

    async def get_assessment_questions(
        self,
        assessment_id: str,
        active_only: bool = True,
    ):
        assessment = await self.assessment_repository.get_by_id(
            assessment_id
        )

        if not assessment:
            raise ValueError(
                "Assessment does not exist."
            )

        return await self.repository.get_by_assessment(
            assessment_id=assessment_id,
            active_only=active_only,
        )

    async def create_question(
        self,
        assessment_id: str,
        question_order: int,
        question_type: str,
        question_text: str,
        options_json: str | None,
        correct_answer: str | None,
        explanation: str | None,
        points: int,
        is_active: bool,
    ):
        assessment = await self.assessment_repository.get_by_id(
            assessment_id
        )

        if not assessment:
            raise ValueError(
                "Assessment does not exist."
            )

        existing = (
            await self.repository.get_by_assessment_and_order(
                assessment_id=assessment_id,
                question_order=question_order,
            )
        )

        if existing:
            raise ValueError(
                "Question with this order already exists "
                "for this assessment."
            )

        return await self.repository.create(
            assessment_id=assessment_id,
            question_order=question_order,
            question_type=question_type,
            question_text=question_text,
            options_json=options_json,
            correct_answer=correct_answer,
            explanation=explanation,
            points=points,
            is_active=is_active,
        )

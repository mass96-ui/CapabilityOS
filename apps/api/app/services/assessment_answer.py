from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.assessment import AssessmentRepository
from app.repositories.assessment_attempt import (
    AssessmentAttemptRepository,
)
from app.repositories.assessment_question import (
    AssessmentQuestionRepository,
)
from app.repositories.assessment_answer import (
    AssessmentAnswerRepository,
)
from app.services.capability_evaluation import CapabilityEvaluationService

from app.repositories.assessment_evidence import (
    AssessmentEvidenceRepository,
)


class AssessmentAnswerService:
    """
    Service responsible for processing answers submitted during
    an assessment.

    Flow:

        User Answer
            â†“
        Validate Answer
            â†“
        Create AssessmentAnswer
            â†“
        Create AssessmentEvidence
            â†“
        Recalculate Assessment Attempt
    """

    def __init__(self, session: AsyncSession):
        self.repository = AssessmentAnswerRepository(session)

        self.attempt_repository = (
            AssessmentAttemptRepository(session)
        )

        self.question_repository = (
            AssessmentQuestionRepository(session)
        )

        self.assessment_repository = (
            AssessmentRepository(session)
        )

        self.evidence_repository = (
            AssessmentEvidenceRepository(session)
        )

        self.capability_evaluation_service = CapabilityEvaluationService(session)

    async def get_answer(
        self,
        answer_id: str,
    ):
        return await self.repository.get_by_id(
            answer_id
        )

    async def get_attempt_answers(
        self,
        attempt_id: str,
    ):
        attempt = await self.attempt_repository.get_by_id(
            attempt_id
        )

        if not attempt:
            raise ValueError(
                "Assessment attempt does not exist."
            )

        return await self.repository.get_by_attempt(
            attempt_id
        )

    async def submit_answer(
        self,
        attempt_id: str,
        question_id: str,
        selected_answer: str,
    ):
        # ==================================================
        # 1. Verify assessment attempt
        # ==================================================

        attempt = await self.attempt_repository.get_by_id(
            attempt_id
        )

        if not attempt:
            raise ValueError(
                "Assessment attempt does not exist."
            )

        if attempt.status != "in_progress":
            raise ValueError(
                "Assessment attempt is no longer active."
            )

        # ==================================================
        # 2. Verify assessment question
        # ==================================================

        question = await self.question_repository.get_by_id(
            question_id
        )

        if not question:
            raise ValueError(
                "Assessment question does not exist."
            )

        if question.assessment_id != attempt.assessment_id:
            raise ValueError(
                "Question does not belong to this assessment."
            )

        if not question.is_active:
            raise ValueError(
                "Assessment question is not active."
            )

        # ==================================================
        # 3. Load assessment
        # ==================================================

        assessment = await self.assessment_repository.get_by_id(
            attempt.assessment_id
        )

        if not assessment:
            raise ValueError(
                "Assessment does not exist."
            )

        # ==================================================
        # 4. Prevent duplicate answer
        # ==================================================

        existing_answer = (
            await self.repository
            .get_by_attempt_and_question(
                attempt_id=attempt_id,
                question_id=question_id,
            )
        )

        if existing_answer:
            raise ValueError(
                "Question has already been answered."
            )

        # ==================================================
        # 5. Evaluate submitted answer
        # ==================================================

        selected = selected_answer.strip()

        correct = (
            question.correct_answer.strip()
            if question.correct_answer
            else None
        )

        is_correct = (
            correct is not None
            and selected.lower() == correct.lower()
        )

        points_earned = (
            question.points
            if is_correct
            else 0
        )

        # ==================================================
        # 6. Create answer record
        # ==================================================

        answer = await self.repository.create(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_answer=selected,
            is_correct=is_correct,
            points_earned=points_earned,
        )

        # ==================================================
        # 7. Create capability evidence
        # ==================================================

        evidence_score = (
            100.0
            if is_correct
            else 0.0
        )

        await self.evidence_repository.create(
            attempt_id=attempt_id,
            answer_id=answer.id,
            user_id=attempt.user_id,
            capability_id=assessment.capability_id,
            evidence_score=evidence_score,
            evidence_weight=float(question.points),
            confidence=1.0,
            evidence_type="assessment",
            evaluator_type="rule_based",
            evaluation_reason=(
                "Correct answer"
                if is_correct
                else "Incorrect answer"
            ),
        )

        # ==================================================
        # 8. Recalculate attempt statistics
        # ==================================================

        answers = await self.repository.get_by_attempt(
            attempt_id
        )

        # Total number of active questions
        question_count = (
            await self.question_repository
            .count_by_assessment(
                assessment.assessment_id
                if hasattr(assessment, "assessment_id")
                else assessment.id
            )
        )

        # Number of questions answered so far
        answered_count = len(answers)

        # Number of correctly answered questions
        correct_count = sum(
            1
            for item in answers
            if item.is_correct
        )

        # Current score
        score = float(
            sum(
                item.points_earned
                for item in answers
            )
        )

        # ==================================================
        # 9. Calculate COMPLETE assessment maximum score
        # ==================================================

        all_questions = (
            await self.question_repository
            .get_by_assessment(
                assessment_id=attempt.assessment_id,
                active_only=True,
            )
        )

        max_score = float(
            sum(
                question.points
                for question in all_questions
            )
        )

        # ==================================================
        # 10. Calculate percentage
        # ==================================================

        percentage = (
            (score / max_score) * 100
            if max_score > 0
            else 0.0
        )

        # ==================================================
        # 11. Update assessment attempt
        # ==================================================

        await self.attempt_repository.update(
            attempt,
            question_count=question_count,
            answered_count=answered_count,
            correct_count=correct_count,
            score=score,
            max_score=max_score,
            percentage=percentage,
        )

        # ==================================================
        # 12. Return submitted answer
        # ==================================================

        return answer

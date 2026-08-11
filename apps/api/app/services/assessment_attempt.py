from __future__ import annotations

from datetime import datetime, timezone

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
from app.repositories.user import UserRepository
from app.services.capability_evaluation import (
    CapabilityEvaluationService,
)


class AssessmentAttemptService:

    def __init__(self, session: AsyncSession):
        self.repository = AssessmentAttemptRepository(session)
        self.assessment_repository = AssessmentRepository(session)
        self.question_repository = AssessmentQuestionRepository(session)
        self.answer_repository = AssessmentAnswerRepository(session)
        self.user_repository = UserRepository(session)

        self.capability_evaluation_service = (
            CapabilityEvaluationService(session)
        )

    # ==========================================================
    # GET ATTEMPT
    # ==========================================================

    async def get_attempt(
        self,
        attempt_id: str,
    ):
        return await self.repository.get_by_id(
            attempt_id
        )

    # ==========================================================
    # GET USER ATTEMPTS
    # ==========================================================

    async def get_user_attempts(
        self,
        user_id: str,
        assessment_id: str | None = None,
    ):
        if assessment_id:
            return await self.repository.get_by_user_and_assessment(
                user_id=user_id,
                assessment_id=assessment_id,
            )

        return await self.repository.get_all(
            filters={
                "user_id": user_id,
            }
        )

    # ==========================================================
    # GET ATTEMPT RESULT
    # ==========================================================

    async def get_attempt_result(
        self,
        attempt_id: str,
    ):
        # --------------------------------------------------
        # 1. Get attempt
        # --------------------------------------------------

        attempt = await self.repository.get_by_id(
            attempt_id
        )

        if not attempt:
            raise ValueError(
                "Assessment attempt does not exist."
            )

        # --------------------------------------------------
        # 2. Result is available only after submission
        # --------------------------------------------------

        if attempt.status != "submitted":
            raise ValueError(
                "Assessment attempt is not submitted."
            )

        # --------------------------------------------------
        # 3. Get assessment
        # --------------------------------------------------

        assessment = await self.assessment_repository.get_by_id(
            attempt.assessment_id
        )

        if not assessment:
            raise ValueError(
                "Assessment does not exist."
            )

        # --------------------------------------------------
        # 4. Get submitted answers
        # --------------------------------------------------

        answers = await self.answer_repository.get_by_attempt(
            attempt_id
        )

        # --------------------------------------------------
        # 5. Get current capability state
        #
        # IMPORTANT:
        # Do NOT call evaluate_capability() here.
        #
        # Capability was already evaluated during submission.
        # Here we only READ the persisted capability state.
        # --------------------------------------------------

        capability = (
            await self.capability_evaluation_service
            .user_capability_repository
            .get_user_capability(
                user_id=attempt.user_id,
                capability_id=assessment.capability_id,
            )
        )

        # --------------------------------------------------
        # 6. Build result response
        # --------------------------------------------------

        return {
            "attempt": {
                "id": attempt.id,
                "user_id": attempt.user_id,
                "assessment_id": attempt.assessment_id,
                "status": attempt.status,
                "question_count": attempt.question_count,
                "answered_count": attempt.answered_count,
                "correct_count": attempt.correct_count,
                "score": attempt.score,
                "max_score": attempt.max_score,
                "percentage": attempt.percentage,
                "started_at": attempt.started_at,
                "submitted_at": attempt.submitted_at,
                "created_at": attempt.created_at,
                "updated_at": attempt.updated_at,
            },

            "answers": [
                {
                    "id": answer.id,
                    "question_id": answer.question_id,
                    "selected_answer": answer.selected_answer,
                    "is_correct": answer.is_correct,
                    "points_earned": answer.points_earned,
                    "answered_at": answer.answered_at,
                }
                for answer in answers
            ],

            "capability": (
                {
                    "user_id": capability.user_id,
                    "capability_id": capability.capability_id,
                    "proficiency_level": capability.proficiency_level,
                    "score": capability.score,
                    "confidence": capability.confidence,
                    "verified": capability.verified,
                    "last_assessed_at": capability.last_assessed_at,
                }
                if capability
                else None
            ),
        }

    # ==========================================================
    # CREATE ATTEMPT
    # ==========================================================

    async def create_attempt(
        self,
        user_id: str,
        assessment_id: str,
    ):
        # --------------------------------------------------
        # Validate user
        # --------------------------------------------------

        user = await self.user_repository.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User does not exist."
            )

        # --------------------------------------------------
        # Validate assessment
        # --------------------------------------------------

        assessment = await self.assessment_repository.get_by_id(
            assessment_id
        )

        if not assessment:
            raise ValueError(
                "Assessment does not exist."
            )

        if not assessment.is_active:
            raise ValueError(
                "Assessment is not active."
            )

        # --------------------------------------------------
        # Count active questions
        # --------------------------------------------------

        question_count = (
            await self.question_repository.count_by_assessment(
                assessment_id=assessment_id,
                active_only=True,
            )
        )

        # --------------------------------------------------
        # Assessment must contain questions
        # --------------------------------------------------

        if question_count == 0:
            raise ValueError(
                "Assessment has no active questions."
            )

        # --------------------------------------------------
        # Create attempt
        # --------------------------------------------------

        return await self.repository.create(
            user_id=user_id,
            assessment_id=assessment_id,
            status="in_progress",
            question_count=question_count,
            answered_count=0,
            correct_count=0,
            score=0,
            max_score=None,
            percentage=0,
        )

    # ==========================================================
    # SUBMIT / FINALIZE ATTEMPT
    # ==========================================================

    async def submit_attempt(
        self,
        attempt_id: str,
    ):
        # --------------------------------------------------
        # 1. Get attempt
        # --------------------------------------------------

        attempt = await self.repository.get_by_id(
            attempt_id
        )

        if not attempt:
            raise ValueError(
                "Assessment attempt does not exist."
            )

        # --------------------------------------------------
        # 2. Prevent duplicate submission
        # --------------------------------------------------

        if attempt.status != "in_progress":
            raise ValueError(
                "Assessment attempt is no longer active."
            )

        # --------------------------------------------------
        # 3. Get active questions
        # --------------------------------------------------

        questions = (
            await self.question_repository.get_by_assessment(
                assessment_id=attempt.assessment_id,
                active_only=True,
            )
        )

        if not questions:
            raise ValueError(
                "Assessment has no active questions."
            )

        # --------------------------------------------------
        # 4. Get answers
        # --------------------------------------------------

        answers = await self.answer_repository.get_by_attempt(
            attempt_id
        )

        # --------------------------------------------------
        # 5. Validate all questions answered
        # --------------------------------------------------

        question_ids = {
            question.id
            for question in questions
        }

        answered_question_ids = {
            answer.question_id
            for answer in answers
        }

        unanswered_question_ids = (
            question_ids - answered_question_ids
        )

        if unanswered_question_ids:
            raise ValueError(
                "Assessment cannot be submitted. "
                f"{len(unanswered_question_ids)} "
                "question(s) are unanswered."
            )

        # --------------------------------------------------
        # 6. Calculate final statistics
        # --------------------------------------------------

        question_count = len(questions)

        answered_count = len(answers)

        correct_count = sum(
            1
            for answer in answers
            if answer.is_correct
        )

        score = float(
            sum(
                answer.points_earned
                for answer in answers
            )
        )

        max_score = float(
            sum(
                question.points
                for question in questions
            )
        )

        percentage = (
            (score / max_score) * 100
            if max_score > 0
            else 0.0
        )

        # --------------------------------------------------
        # 7. Finalize attempt
        # --------------------------------------------------

        await self.repository.update(
            attempt,
            status="submitted",
            question_count=question_count,
            answered_count=answered_count,
            correct_count=correct_count,
            score=score,
            max_score=max_score,
            percentage=percentage,
            submitted_at=datetime.now(timezone.utc),
        )

        # --------------------------------------------------
        # 8. Evaluate capability
        # --------------------------------------------------

        assessment = await self.assessment_repository.get_by_id(
            attempt.assessment_id
        )

        if not assessment:
            raise ValueError(
                "Assessment does not exist."
            )

        capability_result = (
            await self.capability_evaluation_service
            .evaluate_capability(
                user_id=attempt.user_id,
                capability_id=assessment.capability_id,
                attempt_id=attempt.id,
                source="assessment",
                reason="Assessment attempt submitted",
            )
        )

        # --------------------------------------------------
        # 9. Return finalized attempt + capability result
        # --------------------------------------------------

        return {
            "attempt": attempt,
            "capability": capability_result,
        }
import pytest
from sqlalchemy import select

from app.database.session import AsyncSessionFactory
from app.models.user import User
from app.models.capability import Capability
from app.models.assessment import Assessment
from app.models.assessment_question import AssessmentQuestion
from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_evidence import AssessmentEvidence
from app.models.user_capability import UserCapability
from app.models.capability_score_history import CapabilityScoreHistory
from app.services.assessment_attempt import AssessmentAttemptService
from app.services.assessment_answer import AssessmentAnswerService


@pytest.mark.asyncio
async def test_capability_pipeline():
    async with AsyncSessionFactory() as session:

        user = User(
            first_name="Pipeline",
            last_name="Test",
            username="pipeline_test_user",
            email="pipeline@test.local",
            password_hash="test-password-hash",
        )

        capability = Capability(
            name="Python",
            slug="python-pipeline-test",
            category="technical",
        )

        session.add_all([user, capability])
        await session.flush()

        assessment = Assessment(
            capability_id=capability.id,
            title="Python Pipeline Test",
            slug="python-pipeline-test-assessment",
        )

        session.add(assessment)
        await session.flush()

        answers = ["def", "list", "6", "wrong_answer", "len()"]
        correct = ["def", "list", "6", "print", "len()"]

        questions = []

        for i, (answer, expected) in enumerate(
            zip(answers, correct), start=1
        ):
            question = AssessmentQuestion(
                assessment_id=assessment.id,
                question_order=i,
                question_text=f"Pipeline question {i}",
                correct_answer=expected,
                points=1,
            )
            questions.append(question)

        session.add_all(questions)
        await session.flush()

        attempt_service = AssessmentAttemptService(session)

        attempt = await attempt_service.create_attempt(
            user_id=user.id,
            assessment_id=assessment.id,
        )

        answer_service = AssessmentAnswerService(session)

        for question, answer in zip(questions, answers):
            await answer_service.submit_answer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_answer=answer,
            )

        result = await attempt_service.submit_attempt(
            attempt_id=attempt.id
        )

        final_attempt = result["attempt"]
        capability_result = result["capability"]

        evidence_result = await session.execute(
            select(AssessmentEvidence).where(
                AssessmentEvidence.attempt_id == attempt.id
            )
        )
        evidence = evidence_result.scalars().all()

        user_capability_result = await session.execute(
            select(UserCapability).where(
                UserCapability.user_id == user.id,
                UserCapability.capability_id == capability.id,
            )
        )
        user_capability = user_capability_result.scalar_one_or_none()

        history_result = await session.execute(
            select(CapabilityScoreHistory).where(
                CapabilityScoreHistory.user_id == user.id,
                CapabilityScoreHistory.capability_id == capability.id,
            )
        )
        history = history_result.scalars().all()

        assert final_attempt.status == "submitted"
        assert final_attempt.question_count == 5
        assert final_attempt.answered_count == 5
        assert final_attempt.correct_count == 4
        assert final_attempt.score == 4.0
        assert final_attempt.max_score == 5.0
        assert final_attempt.percentage == 80.0

        assert len(evidence) == 5
        assert user_capability is not None
        assert len(history) >= 1

        assert capability_result.score == pytest.approx(80.0)
        assert capability_result.evidence_count == 5

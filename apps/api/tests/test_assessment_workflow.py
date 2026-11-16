import asyncio
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.database.session import AsyncSessionFactory
from app.main import app
from app.models.assessment import Assessment
from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_evidence import AssessmentEvidence
from app.models.assessment_question import AssessmentQuestion
from app.models.capability import Capability
from app.models.user import User


def test_learner_assessment_submission_workflow():
    async def seed():
        async with AsyncSessionFactory() as session:
            suffix = uuid.uuid4().hex[:8]
            learner = User(
                first_name="Learner",
                last_name="One",
                username=f"learner_one_{suffix}",
                email=f"learner.one.{suffix}@test.local",
                password_hash="test-password-hash",
            )
            other_learner = User(
                first_name="Learner",
                last_name="Two",
                username=f"learner_two_{suffix}",
                email=f"learner.two.{suffix}@test.local",
                password_hash="test-password-hash",
            )
            capability = Capability(
                name=f"Workflow capability {suffix}",
                slug=f"workflow-capability-{suffix}",
                category="technical",
            )
            session.add_all([learner, other_learner, capability])
            await session.flush()

            assessment = Assessment(
                capability_id=capability.id,
                title="Workflow assessment",
                slug=f"workflow-assessment-{suffix}",
            )
            session.add(assessment)
            await session.flush()

            question = AssessmentQuestion(
                assessment_id=assessment.id,
                question_order=1,
                question_text="Select the correct answer.",
                options_json='["Correct", "Incorrect"]',
                correct_answer="Correct",
                explanation="The first option is correct.",
                points=1,
            )
            session.add(question)
            await session.flush()
            result = learner.id, other_learner.id, assessment.id, question.id
            await session.commit()
            return result

    learner_id, other_learner_id, assessment_id, question_id = asyncio.run(seed())
    active_user = {"id": learner_id}

    async def override_current_user():
        return User(id=active_user["id"])

    app.dependency_overrides[get_current_user] = override_current_user

    try:
        with TestClient(app) as client:
            question_response = client.get(
                f"/api/v1/assessment-questions/assessment/{assessment_id}"
            )
            assert question_response.status_code == 200
            question_data = question_response.json()[0]
            assert "correct_answer" not in question_data
            assert "explanation" not in question_data

            question_detail_response = client.get(
                f"/api/v1/assessment-questions/{question_id}"
            )
            assert question_detail_response.status_code == 200
            assert "correct_answer" not in question_detail_response.json()
            assert "explanation" not in question_detail_response.json()

            create_response = client.post(
                "/api/v1/assessment-attempts",
                json={
                    "assessment_id": assessment_id,
                    "user_id": other_learner_id,
                },
            )
            assert create_response.status_code == 201
            attempt_id = create_response.json()["id"]
            assert create_response.json()["user_id"] == learner_id

            my_attempts = client.get("/api/v1/assessment-attempts/mine")
            assert my_attempts.status_code == 200
            assert my_attempts.json() == []

            empty_answer_response = client.post(
                "/api/v1/assessment-answers",
                json={
                    "attempt_id": attempt_id,
                    "question_id": question_id,
                    "selected_answer": "   ",
                },
            )
            assert empty_answer_response.status_code == 422
            oversized_answer_response = client.post(
                "/api/v1/assessment-answers",
                json={
                    "attempt_id": attempt_id,
                    "question_id": question_id,
                    "selected_answer": "x" * 501,
                },
            )
            assert oversized_answer_response.status_code == 422

            answer_response = client.post(
                "/api/v1/assessment-answers",
                json={
                    "attempt_id": attempt_id,
                    "question_id": question_id,
                    "selected_answer": "Correct",
                },
            )
            assert answer_response.status_code == 201
            answer_data = answer_response.json()
            assert "is_correct" not in answer_data
            assert "points_earned" not in answer_data
            answer_id = answer_data["id"]

            assert client.get(
                f"/api/v1/assessment-answers/{answer_id}"
            ).status_code == 409
            assert client.get(
                f"/api/v1/assessment-answers/attempt/{attempt_id}"
            ).status_code == 409
            progress_response = client.get(
                f"/api/v1/assessment-attempts/{attempt_id}"
            )
            assert progress_response.status_code == 200
            assert "score" not in progress_response.json()
            assert "correct_count" not in progress_response.json()

            active_user["id"] = other_learner_id
            assert client.get(
                f"/api/v1/assessment-attempts/{attempt_id}"
            ).status_code == 404
            assert client.get(
                f"/api/v1/assessment-attempts/{attempt_id}/result"
            ).status_code == 404
            assert client.post(
                f"/api/v1/assessment-attempts/{attempt_id}/submit"
            ).status_code == 404
            assert client.get(
                f"/api/v1/assessment-answers/{answer_id}"
            ).status_code == 404
            assert client.get(
                f"/api/v1/assessment-answers/attempt/{attempt_id}"
            ).status_code == 404
            assert client.post(
                "/api/v1/assessment-answers",
                json={
                    "attempt_id": attempt_id,
                    "question_id": question_id,
                    "selected_answer": "Incorrect",
                },
            ).status_code == 404
            assert client.get(
                "/api/v1/assessment-attempts/mine"
            ).json() == []

            active_user["id"] = learner_id
            submit_response = client.post(
                f"/api/v1/assessment-attempts/{attempt_id}/submit"
            )
            assert submit_response.status_code == 200
            result_response = client.get(
                f"/api/v1/assessment-attempts/{attempt_id}/result"
            )
            assert result_response.status_code == 200
            result = result_response.json()
            assert result["attempt"]["status"] == "submitted"
            assert result["attempt"]["score"] == 1
            assert result["capability"]["verified"] is False
            submitted_attempts = client.get(
                "/api/v1/assessment-attempts/mine"
            )
            assert [attempt["id"] for attempt in submitted_attempts.json()] == [
                attempt_id
            ]

            submitted_answer_response = client.get(
                f"/api/v1/assessment-answers/{answer_id}"
            )
            assert submitted_answer_response.status_code == 200
            assert submitted_answer_response.json()["is_correct"] is True
            submitted_answers_response = client.get(
                f"/api/v1/assessment-answers/attempt/{attempt_id}"
            )
            assert submitted_answers_response.status_code == 200
            assert len(submitted_answers_response.json()) == 1

        async def verify_evidence():
            async with AsyncSessionFactory() as session:
                attempt = await session.get(AssessmentAttempt, attempt_id)
                evidence_result = await session.execute(
                    select(AssessmentEvidence).where(
                        AssessmentEvidence.attempt_id == attempt_id
                    )
                )
                evidence = evidence_result.scalars().all()
                assert attempt is not None
                assert attempt.user_id == learner_id
                assert len(evidence) == 1
                assert evidence[0].user_id == learner_id
                assert evidence[0].evidence_type == "assessment"
                assert evidence[0].evaluator_type == "rule_based"
                assert evidence[0].evidence_score == 100

        asyncio.run(verify_evidence())

        app.dependency_overrides.pop(get_current_user, None)
        with TestClient(app) as client:
            assert client.get(
                "/api/v1/assessment-attempts/mine"
            ).status_code == 401
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_assessment_bank_writes_require_manager_or_admin():
    async def seed():
        async with AsyncSessionFactory() as session:
            suffix = uuid.uuid4().hex[:8]
            learner = User(
                first_name="Bank",
                last_name="Learner",
                username=f"bank_learner_{suffix}",
                email=f"bank.learner.{suffix}@test.local",
                password_hash="test-password-hash",
            )
            manager = User(
                first_name="Bank",
                last_name="Manager",
                username=f"bank_manager_{suffix}",
                email=f"bank.manager.{suffix}@test.local",
                password_hash="test-password-hash",
                role="manager",
            )
            capability = Capability(
                name=f"Assessment bank capability {suffix}",
                slug=f"assessment-bank-capability-{suffix}",
                category="technical",
            )
            session.add_all([learner, manager, capability])
            await session.flush()

            assessment = Assessment(
                capability_id=capability.id,
                title="Existing learner assessment",
                slug=f"existing-learner-assessment-{suffix}",
            )
            session.add(assessment)
            await session.flush()
            result = learner.id, manager.id, capability.id, assessment.id, suffix
            await session.commit()
            return result

    learner_id, manager_id, capability_id, existing_assessment_id, suffix = (
        asyncio.run(seed())
    )
    active_user = {"id": learner_id, "role": "learner"}
    original_override = app.dependency_overrides.pop(get_current_user, None)

    async def override_current_user():
        return User(
            id=active_user["id"],
            role=active_user["role"],
        )

    try:
        with TestClient(app) as client:
            assessment_payload = {
                "capability_id": capability_id,
                "title": "Manager-created assessment",
                "slug": f"manager-created-assessment-{suffix}",
            }
            question_payload = {
                "assessment_id": existing_assessment_id,
                "question_order": 1,
                "question_text": "Manager-created question",
                "correct_answer": "approved",
            }

            assert client.post(
                "/api/v1/assessments",
                json=assessment_payload,
            ).status_code == 401
            assert client.post(
                "/api/v1/assessment-questions",
                json=question_payload,
            ).status_code == 401

            app.dependency_overrides[get_current_user] = override_current_user
            assert client.post(
                "/api/v1/assessments",
                json=assessment_payload,
            ).status_code == 403
            assert client.post(
                "/api/v1/assessment-questions",
                json=question_payload,
            ).status_code == 403

            assert client.get("/api/v1/assessments").status_code == 200
            assert client.get(
                f"/api/v1/assessment-questions/assessment/{existing_assessment_id}"
            ).status_code == 200

            active_user.update(id=manager_id, role="manager")
            create_assessment_response = client.post(
                "/api/v1/assessments",
                json=assessment_payload,
            )
            assert create_assessment_response.status_code == 201
            created_assessment_id = create_assessment_response.json()["id"]

            question_payload["assessment_id"] = created_assessment_id
            create_question_response = client.post(
                "/api/v1/assessment-questions",
                json=question_payload,
            )
            assert create_question_response.status_code == 201
            assert create_question_response.json()["assessment_id"] == created_assessment_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        if original_override is not None:
            app.dependency_overrides[get_current_user] = original_override

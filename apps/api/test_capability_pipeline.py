import asyncio

from sqlalchemy import select

from app.database.session import AsyncSessionFactory

from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment_evidence import AssessmentEvidence
from app.models.user_capability import UserCapability
from app.models.capability_score_history import CapabilityScoreHistory

from app.services.assessment_answer import AssessmentAnswerService
from app.services.assessment_attempt import AssessmentAttemptService


ATTEMPT_ID = "92fc8690-af94-4b78-ab7e-6ea7ba4b09a8"

QUESTIONS = [
    {
        "question_id": "31b5723e-885d-4afd-8bea-5f447d6c9c43",
        "answer": "def",
    },
    {
        "question_id": "8d069506-4814-4989-aef5-2bffcad1538a",
        "answer": "list",
    },
    {
        "question_id": "6dc764e8-3d52-4a86-9944-3e733ef92348",
        "answer": "6",
    },
    {
        "question_id": "723eb8fd-bcd8-4178-a12c-7c741c46231c",
        "answer": "wrong_answer",
    },
    {
        "question_id": "0f694621-16b6-4d96-baa8-923b0f4e2b21",
        "answer": "len()",
    },
]


async def main():

    print()
    print("=" * 70)
    print("CAPABILITYOS END-TO-END CAPABILITY PIPELINE TEST")
    print("=" * 70)

    async with AsyncSessionFactory() as session:

        # ==================================================
        # 1. Get the test attempt
        # ==================================================

        result = await session.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == ATTEMPT_ID
            )
        )

        attempt = result.scalar_one_or_none()

        if not attempt:
            raise RuntimeError(
                f"Test attempt does not exist: {ATTEMPT_ID}"
            )

        print()
        print("TEST ATTEMPT")
        print("-" * 70)
        print(f"Attempt ID:     {attempt.id}")
        print(f"User ID:        {attempt.user_id}")
        print(f"Assessment ID:  {attempt.assessment_id}")
        print(f"Status:         {attempt.status}")

        if attempt.status != "in_progress":
            raise RuntimeError(
                f"Attempt is not available for testing. "
                f"Current status: {attempt.status}"
            )

        # ==================================================
        # 2. Create answer service
        # ==================================================

        answer_service = AssessmentAnswerService(session)

        # ==================================================
        # 3. Submit all five answers
        # ==================================================

        print()
        print("SUBMITTING ANSWERS")
        print("-" * 70)

        for index, item in enumerate(QUESTIONS, start=1):

            answer = await answer_service.submit_answer(
                attempt_id=ATTEMPT_ID,
                question_id=item["question_id"],
                selected_answer=item["answer"],
            )

            print(
                f"Question {index}: "
                f"selected={answer.selected_answer!r} | "
                f"correct={answer.is_correct} | "
                f"points={answer.points_earned}"
            )

        # ==================================================
        # 4. Finalize assessment
        # ==================================================

        print()
        print("FINALIZING ASSESSMENT")
        print("-" * 70)

        attempt_service = AssessmentAttemptService(session)

        final_result = await attempt_service.submit_attempt(
            attempt_id=ATTEMPT_ID
        )

        final_attempt = final_result["attempt"]
        capability_result = final_result["capability"]

        print(f"Status:          {final_attempt.status}")
        print(f"Questions:       {final_attempt.question_count}")
        print(f"Answered:        {final_attempt.answered_count}")
        print(f"Correct:         {final_attempt.correct_count}")
        print(f"Score:           {final_attempt.score}")
        print(f"Max Score:       {final_attempt.max_score}")
        print(f"Percentage:      {final_attempt.percentage}")

        # ==================================================
        # 5. Capability result
        # ==================================================

        print()
        print("CAPABILITY RESULT")
        print("-" * 70)

        print(f"User ID:         {capability_result.user_id}")
        print(f"Capability ID:   {capability_result.capability_id}")
        print(f"Score:           {capability_result.score}")
        print(f"Proficiency:     {capability_result.proficiency}")
        print(
            f"Proficiency Level: "
            f"{capability_result.proficiency_level}"
        )
        print(f"Confidence:      {capability_result.confidence}")
        print(f"Evidence Count:  {capability_result.evidence_count}")

        # ==================================================
        # 6. Verify evidence
        # ==================================================

        evidence_result = await session.execute(
            select(AssessmentEvidence).where(
                AssessmentEvidence.attempt_id == ATTEMPT_ID
            )
        )

        evidence = evidence_result.scalars().all()

        print()
        print("CAPABILITY EVIDENCE")
        print("-" * 70)
        print(f"Evidence records: {len(evidence)}")

        for item in evidence:
            print(
                f"Evidence ID={item.id} | "
                f"score={item.evidence_score} | "
                f"weight={item.evidence_weight} | "
                f"confidence={item.confidence}"
            )

        # ==================================================
        # 7. Verify UserCapability
        # ==================================================

        user_capability_result = await session.execute(
            select(UserCapability).where(
                UserCapability.user_id == final_attempt.user_id,
                UserCapability.capability_id
                == capability_result.capability_id,
            )
        )

        user_capability = (
            user_capability_result.scalar_one_or_none()
        )

        print()
        print("USER CAPABILITY")
        print("-" * 70)

        if user_capability:
            print(f"User ID:          {user_capability.user_id}")
            print(
                f"Capability ID:    "
                f"{user_capability.capability_id}"
            )
            print(
                f"Score:            "
                f"{user_capability.score}"
            )
            print(
                f"Proficiency:      "
                f"{user_capability.proficiency_level}"
            )
            print(
                f"Confidence:       "
                f"{user_capability.confidence}"
            )
            print(
                f"Verified:         "
                f"{user_capability.verified}"
            )
        else:
            print("ERROR: UserCapability was not created.")

        # ==================================================
        # 8. Verify capability history
        # ==================================================

        history_result = await session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.user_id
                == final_attempt.user_id,
                CapabilityScoreHistory.capability_id
                == capability_result.capability_id,
            )
            .order_by(
                CapabilityScoreHistory.created_at.desc()
            )
        )

        history = history_result.scalars().all()

        print()
        print("CAPABILITY SCORE HISTORY")
        print("-" * 70)
        print(f"History records: {len(history)}")

        for item in history:
            print(
                f"History ID={item.id} | "
                f"score={item.score} | "
                f"previous={item.previous_score} | "
                f"delta={item.score_delta} | "
                f"source={item.source}"
            )

        # ==================================================
        # 9. Automated assertions
        # ==================================================

        print()
        print("VALIDATION")
        print("-" * 70)

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

        assert capability_result.score == 80.0
        assert capability_result.evidence_count == 5

        print("Assessment finalization:       PASS")
        print("Answer evaluation:             PASS")
        print("Evidence creation:             PASS")
        print("Capability scoring:            PASS")
        print("Capability evaluation:         PASS")
        print("UserCapability persistence:    PASS")
        print("Capability history persistence: PASS")

        print()
        print("=" * 70)
        print("FULL CAPABILITY PIPELINE TEST: PASS")
        print("=" * 70)
        print()


if __name__ == "__main__":
    asyncio.run(main())
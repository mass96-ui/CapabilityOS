from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import LearnerDep
from app.database.session import get_session
from app.schemas.assessment_answer import (
    AssessmentAnswerCreate,
    AssessmentAnswerResponse,
)
from app.services.assessment_answer import (
    AssessmentAnswerService,
)
from app.services.assessment_attempt import AssessmentAttemptService

router = APIRouter()


async def _require_owned_attempt(
    attempt_id: str,
    current_user: LearnerDep,
    service: AssessmentAttemptService,
):
    attempt = await service.get_attempt(attempt_id=attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment attempt does not exist.",
        )
    return attempt


@router.get(
    "/{answer_id}",
    response_model=AssessmentAnswerResponse,
)
async def get_answer(
    answer_id: str,
    current_user: LearnerDep,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAnswerService(session)

    answer = await service.get_answer(answer_id)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment answer not found.",
        )

    attempt = await _require_owned_attempt(
        answer.attempt_id,
        current_user,
        AssessmentAttemptService(session),
    )
    if attempt.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answers are available after the assessment is submitted.",
        )

    return answer


@router.get(
    "/attempt/{attempt_id}",
    response_model=list[AssessmentAnswerResponse],
)
async def get_attempt_answers(
    attempt_id: str,
    current_user: LearnerDep,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAnswerService(session)

    try:
        attempt = await _require_owned_attempt(
            attempt_id,
            current_user,
            AssessmentAttemptService(session),
        )
        if attempt.status != "submitted":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Answers are available after the assessment is submitted.",
            )
        return await service.get_attempt_answers(
            attempt_id=attempt_id,
        )

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/",
    response_model=AssessmentAnswerResponse,
    response_model_exclude={"is_correct", "points_earned"},
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    payload: AssessmentAnswerCreate,
    current_user: LearnerDep,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAnswerService(session)

    try:
        await _require_owned_attempt(
            payload.attempt_id,
            current_user,
            AssessmentAttemptService(session),
        )
        return await service.submit_answer(
            attempt_id=payload.attempt_id,
            question_id=payload.question_id,
            selected_answer=payload.selected_answer,
        )

    except HTTPException:
        raise
    except ValueError as exc:
        message = str(exc)

        if "already been answered" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

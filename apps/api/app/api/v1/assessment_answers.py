from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.assessment_answer import (
    AssessmentAnswerCreate,
    AssessmentAnswerResponse,
)
from app.services.assessment_answer import (
    AssessmentAnswerService,
)

router = APIRouter()


@router.get(
    "/{answer_id}",
    response_model=AssessmentAnswerResponse,
)
async def get_answer(
    answer_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAnswerService(session)

    answer = await service.get_answer(answer_id)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment answer not found.",
        )

    return answer


@router.get(
    "/attempt/{attempt_id}",
    response_model=list[AssessmentAnswerResponse],
)
async def get_attempt_answers(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAnswerService(session)

    try:
        return await service.get_attempt_answers(
            attempt_id=attempt_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/",
    response_model=AssessmentAnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    payload: AssessmentAnswerCreate,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAnswerService(session)

    try:
        return await service.submit_answer(
            attempt_id=payload.attempt_id,
            question_id=payload.question_id,
            selected_answer=payload.selected_answer,
        )

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

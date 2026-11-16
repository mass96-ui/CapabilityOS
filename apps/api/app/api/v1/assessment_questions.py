from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import ManagerDep
from app.database.session import get_session
from app.schemas.assessment_question import (
    AssessmentQuestionCreate,
    AssessmentQuestionForAttemptResponse,
    AssessmentQuestionResponse,
)
from app.services.assessment_question import (
    AssessmentQuestionService,
)

router = APIRouter()


@router.get(
    "/{question_id}",
    response_model=AssessmentQuestionForAttemptResponse,
)
async def get_question(
    question_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentQuestionService(session)

    question = await service.get_question(question_id)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment question not found.",
        )

    return question


@router.get(
    "/assessment/{assessment_id}",
    response_model=list[AssessmentQuestionForAttemptResponse],
)
async def get_assessment_questions(
    assessment_id: str,
    active_only: bool = True,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentQuestionService(session)

    try:
        return await service.get_assessment_questions(
            assessment_id=assessment_id,
            active_only=active_only,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/",
    response_model=AssessmentQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    payload: AssessmentQuestionCreate,
    current_user: ManagerDep,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentQuestionService(session)

    try:
        return await service.create_question(
            assessment_id=payload.assessment_id,
            question_order=payload.question_order,
            question_type=payload.question_type,
            question_text=payload.question_text,
            options_json=payload.options_json,
            correct_answer=payload.correct_answer,
            explanation=payload.explanation,
            points=payload.points,
            is_active=payload.is_active,
        )

    except ValueError as exc:
        message = str(exc)

        if "order already exists" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

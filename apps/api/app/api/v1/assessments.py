from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
)
from app.services.assessment import AssessmentService


router = APIRouter()


@router.get(
    "/",
    response_model=list[AssessmentResponse],
)
async def get_assessments(
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentService(session)

    return await service.get_assessments()


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
async def get_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentService(session)

    assessment = await service.get_assessment(
        assessment_id
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    return assessment


@router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    payload: AssessmentCreate,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentService(session)

    try:
        return await service.create(
            capability_id=payload.capability_id,
            title=payload.title,
            slug=payload.slug,
            description=payload.description,
            difficulty=payload.difficulty,
            time_limit_minutes=payload.time_limit_minutes,
            is_active=payload.is_active,
        )

    except ValueError as exc:
        message = str(exc)

        if "slug already exists" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

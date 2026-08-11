from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.assessment_attempt import (
    AssessmentAttemptCreate,
    AssessmentAttemptResponse,
    AssessmentAttemptSubmitResponse,
)
from app.services.assessment_attempt import (
    AssessmentAttemptService,
)

router = APIRouter()


# ==========================================================
# GET ATTEMPT RESULT
# ==========================================================

@router.get(
    "/{attempt_id}/result",
)
async def get_attempt_result(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAttemptService(session)

    try:
        return await service.get_attempt_result(
            attempt_id=attempt_id,
        )

    except ValueError as exc:
        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if "not submitted" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# ==========================================================
# GET ATTEMPT
# ==========================================================

@router.get(
    "/{attempt_id}",
    response_model=AssessmentAttemptResponse,
)
async def get_attempt(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAttemptService(session)

    attempt = await service.get_attempt(
        attempt_id=attempt_id,
    )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment attempt does not exist.",
        )

    return attempt


# ==========================================================
# GET USER ATTEMPTS
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[AssessmentAttemptResponse],
)
async def get_user_attempts(
    user_id: str,
    assessment_id: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAttemptService(session)

    return await service.get_user_attempts(
        user_id=user_id,
        assessment_id=assessment_id,
    )


# ==========================================================
# CREATE ATTEMPT
# ==========================================================

@router.post(
    "/",
    response_model=AssessmentAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_attempt(
    payload: AssessmentAttemptCreate,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAttemptService(session)

    try:
        return await service.create_attempt(
            user_id=payload.user_id,
            assessment_id=payload.assessment_id,
        )

    except ValueError as exc:
        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if "not active" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        if "no active questions" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# ==========================================================
# SUBMIT / FINALIZE ATTEMPT
# ==========================================================

@router.post(
    "/{attempt_id}/submit",
    response_model=AssessmentAttemptSubmitResponse,
)
async def submit_attempt(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = AssessmentAttemptService(session)

    try:
        return await service.submit_attempt(
            attempt_id=attempt_id,
        )

    except ValueError as exc:
        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if "no longer active" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        if "no active questions" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        if "cannot be submitted" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
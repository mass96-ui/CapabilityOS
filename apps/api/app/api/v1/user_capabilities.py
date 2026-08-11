from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.user_capability import (
    UserCapabilityCreate,
    UserCapabilityResponse,
)
from app.services.user_capability import UserCapabilityService


router = APIRouter()


@router.get(
    "/{user_id}/capabilities",
    response_model=list[UserCapabilityResponse],
)
async def get_user_capabilities(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):

    service = UserCapabilityService(session)

    return await service.get_user_capabilities(
        user_id
    )


@router.post(
    "/{user_id}/capabilities",
    response_model=UserCapabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_user_capability(
    user_id: str,
    payload: UserCapabilityCreate,
    session: AsyncSession = Depends(get_session),
):

    service = UserCapabilityService(session)

    try:

        return await service.create(
            user_id=user_id,
            capability_id=payload.capability_id,
            proficiency_level=payload.proficiency_level,
            score=payload.score,
            confidence=payload.confidence,
            verified=payload.verified,
        )

    except ValueError as exc:

        message = str(exc)

        if "already has" in message:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

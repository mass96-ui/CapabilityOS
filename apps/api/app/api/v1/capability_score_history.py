from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database.session import get_session
from app.schemas.capability_score_history import (
    CapabilityScoreHistoryResponse,
)
from app.services.capability_score_history import (
    CapabilityScoreHistoryService,
)


router = APIRouter(
    prefix="/capability-history",
    tags=["Capability Score History"],
)


@router.get(
    "/{history_id}",
    response_model=CapabilityScoreHistoryResponse,
)
async def get_history(
    history_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityScoreHistoryService(session)

    history = await service.get_by_id(history_id)

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability score history not found.",
        )

    return history


@router.get(
    "/user/{user_id}",
    response_model=list[CapabilityScoreHistoryResponse],
)
async def get_user_history(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityScoreHistoryService(session)

    return await service.get_by_user(user_id)


@router.get(
    "/user/{user_id}/capability/{capability_id}",
    response_model=list[CapabilityScoreHistoryResponse],
)
async def get_user_capability_history(
    user_id: str,
    capability_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityScoreHistoryService(session)

    return await service.get_user_capability_history(
        user_id,
        capability_id,
    )


@router.get(
    "/attempt/{attempt_id}",
    response_model=list[CapabilityScoreHistoryResponse],
)
async def get_attempt_history(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityScoreHistoryService(session)

    return await service.get_by_attempt(attempt_id)

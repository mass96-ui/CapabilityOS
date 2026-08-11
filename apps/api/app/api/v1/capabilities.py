from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.capability import CapabilityCreate, CapabilityResponse
from app.services.capability import CapabilityService


router = APIRouter()


@router.get(
    "/",
    response_model=list[CapabilityResponse],
)
async def list_capabilities(
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityService(session)
    return await service.get_all()


@router.get(
    "/{capability_id}",
    response_model=CapabilityResponse,
)
async def get_capability(
    capability_id: str,
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityService(session)

    capability = await service.get_by_id(capability_id)

    if not capability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability not found.",
        )

    return capability


@router.post(
    "/",
    response_model=CapabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_capability(
    payload: CapabilityCreate,
    session: AsyncSession = Depends(get_session),
):
    service = CapabilityService(session)

    try:
        return await service.create(
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            category=payload.category,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

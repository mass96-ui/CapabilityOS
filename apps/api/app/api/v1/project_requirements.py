from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.project_requirement import (
    ProjectRequirementCreate,
    ProjectRequirementResponse,
    ProjectRequirementUpdate,
)
from app.services.project_requirement import (
    ProjectRequirementService,
)


router = APIRouter()


# ==========================================================
# CREATE PROJECT REQUIREMENT
# ==========================================================

@router.post(
    "/{project_id}/requirements",
    response_model=ProjectRequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_requirement(
    project_id: str,
    payload: ProjectRequirementCreate,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectRequirementService(
        session
    )

    if payload.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID in body does not match project ID in URL.",
        )

    try:

        return await service.create_requirement(
            project_id=project_id,
            capability_id=payload.capability_id,
            description=payload.description,
            minimum_proficiency_level=(
                payload.minimum_proficiency_level
            ),
            importance=payload.importance,
            required=payload.required,
        )

    except ValueError as exc:

        message = str(exc)

        if "does not exist" in message:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# ==========================================================
# GET PROJECT REQUIREMENTS
# ==========================================================

@router.get(
    "/{project_id}/requirements",
    response_model=list[ProjectRequirementResponse],
)
async def get_project_requirements(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectRequirementService(
        session
    )

    try:

        return await service.get_project_requirements(
            project_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# GET REQUIREMENT
# ==========================================================

@router.get(
    "/requirements/{requirement_id}",
    response_model=ProjectRequirementResponse,
)
async def get_project_requirement(
    requirement_id: str,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectRequirementService(
        session
    )

    try:

        return await service.get_requirement(
            requirement_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# UPDATE REQUIREMENT
# ==========================================================

@router.patch(
    "/requirements/{requirement_id}",
    response_model=ProjectRequirementResponse,
)
async def update_project_requirement(
    requirement_id: str,
    payload: ProjectRequirementUpdate,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectRequirementService(
        session
    )

    try:

        return await service.update_requirement(
            requirement_id,
            description=payload.description,
            minimum_proficiency_level=(
                payload.minimum_proficiency_level
            ),
            importance=payload.importance,
            required=payload.required,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# DELETE REQUIREMENT
# ==========================================================

@router.delete(
    "/requirements/{requirement_id}",
)
async def delete_project_requirement(
    requirement_id: str,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectRequirementService(
        session
    )

    try:

        return await service.delete_requirement(
            requirement_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
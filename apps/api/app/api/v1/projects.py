from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUserDep, ManagerDep, get_current_user
from app.database.session import get_session
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService


router = APIRouter()


# ==========================================================
# CREATE PROJECT
# ==========================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    payload: ProjectCreate,
    current_user: ManagerDep,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectService(
        session,
        current_user=current_user,
    )

    try:

        return await service.create_project(
            name=payload.name,
            description=payload.description,
            project_type=payload.project_type,
            owner_id=payload.owner_id,
            organization_id=payload.organization_id,
        )

    except ValueError as exc:

        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if "permission" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# ==========================================================
# GET ALL PROJECTS
# ==========================================================

@router.get(
    "",
    response_model=list[ProjectResponse],
)
async def get_projects(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    status: str | None = Query(None, max_length=30),
    project_type: str | None = Query(None, max_length=50),
    q: str | None = Query(None, max_length=100),
):

    service = ProjectService(session)

    return await service.get_projects(
        status=status,
        project_type=project_type,
        search_query=q,
    )


# ==========================================================
# GET PROJECTS BY OWNER
# ==========================================================

@router.get(
    "/owner/{owner_id}",
    response_model=list[ProjectResponse],
)
async def get_owner_projects(
    owner_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    service = ProjectService(session)

    try:

        return await service.get_owner_projects(
            owner_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# GET PROJECT
# ==========================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    service = ProjectService(session)

    try:

        return await service.get_project(
            project_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ==========================================================
# UPDATE PROJECT
# ==========================================================

@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: ManagerDep,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectService(
        session,
        current_user=current_user,
    )

    try:

        return await service.update_project(
            project_id,
            name=payload.name,
            description=payload.description,
            status=payload.status,
            project_type=payload.project_type,
        )

    except ValueError as exc:

        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if "permission" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# ==========================================================
# DELETE PROJECT
# ==========================================================

@router.delete(
    "/{project_id}",
)
async def delete_project(
    project_id: str,
    current_user: ManagerDep,
    session: AsyncSession = Depends(get_session),
):

    service = ProjectService(
        session,
        current_user=current_user,
    )

    try:

        return await service.delete_project(
            project_id
        )

    except ValueError as exc:

        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if "permission" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
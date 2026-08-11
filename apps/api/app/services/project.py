from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository


class ProjectService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = ProjectRepository(session)
        self.user_repository = UserRepository(session)

    # ======================================================
    # CREATE PROJECT
    # ======================================================

    async def create_project(
        self,
        *,
        name: str,
        description: str | None,
        project_type: str,
        owner_id: str,
        organization_id: str | None,
    ):

        owner = await self.user_repository.get_by_id(
            owner_id
        )

        if not owner:
            raise ValueError(
                "Project owner does not exist."
            )

        return await self.repository.create(
            name=name,
            description=description,
            project_type=project_type,
            owner_id=owner_id,
            organization_id=organization_id,
        )

    # ======================================================
    # GET PROJECT
    # ======================================================

    async def get_project(
        self,
        project_id: str,
    ):

        project = await self.repository.get_by_id(
            project_id
        )

        if not project:
            raise ValueError(
                "Project does not exist."
            )

        return project

    # ======================================================
    # GET ALL PROJECTS
    # ======================================================

    async def get_projects(
        self,
    ):

        return await self.repository.get_all()

    # ======================================================
    # GET OWNER PROJECTS
    # ======================================================

    async def get_owner_projects(
        self,
        owner_id: str,
    ):

        owner = await self.user_repository.get_by_id(
            owner_id
        )

        if not owner:
            raise ValueError(
                "Project owner does not exist."
            )

        return await self.repository.get_by_owner(
            owner_id
        )

    # ======================================================
    # UPDATE PROJECT
    # ======================================================

    async def update_project(
        self,
        project_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        project_type: str | None = None,
    ):

        project = await self.get_project(
            project_id
        )

        allowed_statuses = {
            "draft",
            "open",
            "planning",
            "active",
            "paused",
            "completed",
            "cancelled",
            "archived",
        }

        if status is not None and status not in allowed_statuses:
            raise ValueError(
                "Invalid project status."
            )

        return await self.repository.update(
            project,
            name=name,
            description=description,
            status=status,
            project_type=project_type,
        )

    # ======================================================
    # DELETE PROJECT
    # ======================================================

    async def delete_project(
        self,
        project_id: str,
    ):

        project = await self.get_project(
            project_id
        )

        await self.repository.delete(
            project
        )

        return {
            "success": True,
            "project_id": project_id,
        }
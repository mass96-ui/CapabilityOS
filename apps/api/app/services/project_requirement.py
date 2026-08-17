from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.capability import CapabilityRepository
from app.repositories.project import ProjectRepository
from app.repositories.project_requirement import (
    ProjectRequirementRepository,
)


class ProjectRequirementService:

    def __init__(
        self,
        session: AsyncSession,
        current_user: User | None = None,
    ):

        self.repository = ProjectRequirementRepository(
            session
        )

        self.project_repository = ProjectRepository(
            session
        )

        self.capability_repository = CapabilityRepository(
            session
        )

        self.current_user = current_user

    def _require_owner_or_admin(self, project) -> None:
        """
        Ensure the current user is the project owner or an admin.
        """

        if self.current_user is None:
            raise ValueError(
                "Authentication required."
            )

        is_admin = (
            self.current_user.is_superuser
            or self.current_user.role == "admin"
        )

        if is_admin:
            return

        if project.owner_id == self.current_user.id:
            return

        raise ValueError(
            "You do not have permission to modify this project."
        )

    # ======================================================
    # CREATE REQUIREMENT
    # ======================================================

    async def create_requirement(
        self,
        *,
        project_id: str,
        capability_id: str,
        description: str | None,
        minimum_proficiency_level: int,
        importance: float,
        required: bool,
    ):

        project = await self.project_repository.get_by_id(
            project_id
        )

        if not project:
            raise ValueError(
                "Project does not exist."
            )

        self._require_owner_or_admin(project)

        capability = await self.capability_repository.get_by_id(
            capability_id
        )

        if not capability:
            raise ValueError(
                "Capability does not exist."
            )

        existing = (
            await self.repository
            .get_by_project_and_capability(
                project_id,
                capability_id,
            )
        )

        if existing:
            raise ValueError(
                "This capability is already required by the project."
            )

        return await self.repository.create(
            project_id=project_id,
            capability_id=capability_id,
            description=description,
            minimum_proficiency_level=minimum_proficiency_level,
            importance=importance,
            required=required,
        )

    # ======================================================
    # GET REQUIREMENT
    # ======================================================

    async def get_requirement(
        self,
        requirement_id: str,
    ):

        requirement = (
            await self.repository.get_by_id(
                requirement_id
            )
        )

        if not requirement:
            raise ValueError(
                "Project requirement does not exist."
            )

        capability = await self.capability_repository.get_by_id(
            requirement.capability_id
        )

        requirement.capability_name = capability.name if capability else None

        return requirement

    # ======================================================
    # GET PROJECT REQUIREMENTS
    # ======================================================

    async def get_project_requirements(
        self,
        project_id: str,
    ):

        project = await self.project_repository.get_by_id(
            project_id
        )

        if not project:
            raise ValueError(
                "Project does not exist."
            )

        requirements = await self.repository.get_by_project(
            project_id
        )

        capability_ids = [
            req.capability_id for req in requirements
        ]

        capabilities = {}
        if capability_ids:
            for cid in capability_ids:
                cap = await self.capability_repository.get_by_id(
                    cid
                )
                if cap:
                    capabilities[cid] = cap.name

        for req in requirements:
            req.capability_name = capabilities.get(
                req.capability_id
            )

        return requirements

    # ======================================================
    # UPDATE
    # ======================================================

    async def update_requirement(
        self,
        requirement_id: str,
        *,
        description: str | None = None,
        minimum_proficiency_level: int | None = None,
        importance: float | None = None,
        required: bool | None = None,
    ):

        requirement = await self.get_requirement(
            requirement_id
        )

        project = await self.project_repository.get_by_id(
            requirement.project_id
        )

        if not project:
            raise ValueError(
                "Project does not exist."
            )

        self._require_owner_or_admin(project)

        return await self.repository.update(
            requirement,
            description=description,
            minimum_proficiency_level=minimum_proficiency_level,
            importance=importance,
            required=required,
        )

    # ======================================================
    # DELETE
    # ======================================================

    async def delete_requirement(
        self,
        requirement_id: str,
    ):

        requirement = await self.get_requirement(
            requirement_id
        )

        project = await self.project_repository.get_by_id(
            requirement.project_id
        )

        if not project:
            raise ValueError(
                "Project does not exist."
            )

        self._require_owner_or_admin(project)

        await self.repository.delete(
            requirement
        )

        return {
            "success": True,
            "requirement_id": requirement_id,
        }
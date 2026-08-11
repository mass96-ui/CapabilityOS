from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_requirement import ProjectRequirement


class ProjectRequirementRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # ======================================================
    # CREATE
    # ======================================================

    async def create(
        self,
        *,
        project_id: str,
        capability_id: str,
        description: str | None,
        minimum_proficiency_level: int,
        importance: float,
        required: bool,
    ) -> ProjectRequirement:

        requirement = ProjectRequirement(
            project_id=project_id,
            capability_id=capability_id,
            description=description,
            minimum_proficiency_level=minimum_proficiency_level,
            importance=importance,
            required=required,
        )

        self.session.add(requirement)

        await self.session.commit()

        await self.session.refresh(requirement)

        return requirement

    # ======================================================
    # GET BY ID
    # ======================================================

    async def get_by_id(
        self,
        requirement_id: str,
    ) -> ProjectRequirement | None:

        result = await self.session.execute(
            select(ProjectRequirement).where(
                ProjectRequirement.id == requirement_id
            )
        )

        return result.scalar_one_or_none()

    # ======================================================
    # GET PROJECT REQUIREMENTS
    # ======================================================

    async def get_by_project(
        self,
        project_id: str,
    ) -> list[ProjectRequirement]:

        result = await self.session.execute(
            select(ProjectRequirement)
            .where(
                ProjectRequirement.project_id == project_id
            )
            .order_by(
                ProjectRequirement.created_at.asc()
            )
        )

        return list(result.scalars().all())

    # ======================================================
    # GET PROJECT + CAPABILITY
    # ======================================================

    async def get_by_project_and_capability(
        self,
        project_id: str,
        capability_id: str,
    ) -> ProjectRequirement | None:

        result = await self.session.execute(
            select(ProjectRequirement).where(
                ProjectRequirement.project_id == project_id,
                ProjectRequirement.capability_id == capability_id,
            )
        )

        return result.scalar_one_or_none()

    # ======================================================
    # UPDATE
    # ======================================================

    async def update(
        self,
        requirement: ProjectRequirement,
        **values,
    ) -> ProjectRequirement:

        for key, value in values.items():

            if value is not None:
                setattr(
                    requirement,
                    key,
                    value,
                )

        await self.session.commit()

        await self.session.refresh(requirement)

        return requirement

    # ======================================================
    # DELETE
    # ======================================================

    async def delete(
        self,
        requirement: ProjectRequirement,
    ) -> None:

        await self.session.delete(requirement)

        await self.session.commit()
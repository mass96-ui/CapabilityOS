from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        project_type: str,
        owner_id: str,
        organization_id: str | None,
    ) -> Project:

        project = Project(
            name=name,
            description=description,
            project_type=project_type,
            owner_id=owner_id,
            organization_id=organization_id,
            status="draft",
        )

        self.session.add(project)

        await self.session.commit()

        await self.session.refresh(project)

        return project

    async def get_by_id(
        self,
        project_id: str,
    ) -> Project | None:

        result = await self.session.execute(
            select(Project).where(
                Project.id == project_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_owner(
        self,
        owner_id: str,
    ) -> list[Project]:

        result = await self.session.execute(
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_all(self) -> list[Project]:

        result = await self.session.execute(
            select(Project)
            .order_by(Project.created_at.desc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        project: Project,
        **values,
    ) -> Project:

        for key, value in values.items():
            if value is not None:
                setattr(project, key, value)

        await self.session.commit()

        await self.session.refresh(project)

        return project

    async def delete(
        self,
        project: Project,
    ) -> None:

        await self.session.delete(project)

        await self.session.commit()
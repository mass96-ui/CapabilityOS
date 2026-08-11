from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment


class AssessmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        assessment_id: str,
    ) -> Assessment | None:
        result = await self.session.execute(
            select(Assessment).where(
                Assessment.id == assessment_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Assessment | None:
        result = await self.session.execute(
            select(Assessment).where(
                Assessment.slug == slug
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        active_only: bool = True,
    ) -> list[Assessment]:
        query = select(Assessment)

        if active_only:
            query = query.where(
                Assessment.is_active.is_(True)
            )

        query = query.order_by(
            Assessment.created_at.desc()
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def create(
        self,
        capability_id: str,
        title: str,
        slug: str,
        description: str | None,
        difficulty: str,
        time_limit_minutes: int | None,
        is_active: bool,
    ) -> Assessment:
        assessment = Assessment(
            capability_id=capability_id,
            title=title,
            slug=slug,
            description=description,
            difficulty=difficulty,
            time_limit_minutes=time_limit_minutes,
            is_active=is_active,
        )

        self.session.add(assessment)

        await self.session.commit()
        await self.session.refresh(assessment)

        return assessment

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.assessment import AssessmentRepository
from app.repositories.capability import CapabilityRepository


class AssessmentService:
    def __init__(self, session: AsyncSession):
        self.repository = AssessmentRepository(session)
        self.capability_repository = CapabilityRepository(session)

    async def get_assessment(
        self,
        assessment_id: str,
    ):
        return await self.repository.get_by_id(
            assessment_id
        )

    async def get_assessments(
        self,
        active_only: bool = True,
    ):
        return await self.repository.get_all(
            active_only=active_only
        )

    async def create(
        self,
        capability_id: str,
        title: str,
        slug: str,
        description: str | None,
        difficulty: str,
        time_limit_minutes: int | None,
        is_active: bool,
    ):
        capability = await self.capability_repository.get_by_id(
            capability_id
        )

        if not capability:
            raise ValueError(
                "Capability does not exist."
            )

        existing = await self.repository.get_by_slug(
            slug
        )

        if existing:
            raise ValueError(
                "Assessment with this slug already exists."
            )

        return await self.repository.create(
            capability_id=capability_id,
            title=title,
            slug=slug,
            description=description,
            difficulty=difficulty,
            time_limit_minutes=time_limit_minutes,
            is_active=is_active,
        )

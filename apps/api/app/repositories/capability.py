from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capability import Capability


class CapabilityRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, capability_id: str) -> Capability | None:
        result = await self.session.execute(
            select(Capability).where(Capability.id == capability_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Capability | None:
        result = await self.session.execute(
            select(Capability).where(Capability.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Capability]:
        result = await self.session.execute(
            select(Capability)
            .where(Capability.is_active.is_(True))
            .order_by(Capability.name)
        )
        return list(result.scalars().all())

    async def create(
        self,
        name: str,
        slug: str,
        description: str | None,
        category: str,
    ) -> Capability:

        capability = Capability(
            name=name,
            slug=slug,
            description=description,
            category=category,
        )

        self.session.add(capability)
        await self.session.commit()
        await self.session.refresh(capability)

        return capability

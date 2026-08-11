from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.capability import CapabilityRepository


class CapabilityService:

    def __init__(self, session: AsyncSession):
        self.repository = CapabilityRepository(session)

    async def get_all(self):
        return await self.repository.get_all()

    async def get_by_id(self, capability_id: str):
        return await self.repository.get_by_id(capability_id)

    async def create(
        self,
        name: str,
        slug: str,
        description: str | None,
        category: str,
    ):
        existing = await self.repository.get_by_slug(slug)

        if existing:
            raise ValueError("Capability with this slug already exists.")

        return await self.repository.create(
            name=name,
            slug=slug,
            description=description,
            category=category,
        )

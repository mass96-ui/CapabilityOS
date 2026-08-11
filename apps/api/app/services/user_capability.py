from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.capability import CapabilityRepository
from app.repositories.user_capability import UserCapabilityRepository


class UserCapabilityService:
    """
    Service responsible for managing a user's current capability state.

    UserCapability stores the latest measured capability representation.
    Historical measurements are maintained separately by the capability
    score history subsystem.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserCapabilityRepository(session)
        self.capability_repository = CapabilityRepository(session)

    async def get_user_capabilities(
        self,
        user_id: str,
    ):
        return await self.repository.get_user_capabilities(
            user_id=user_id,
        )

    async def get_user_capability(
        self,
        user_id: str,
        capability_id: str,
    ):
        return await self.repository.get_user_capability(
            user_id=user_id,
            capability_id=capability_id,
        )

    async def create(
        self,
        user_id: str,
        capability_id: str,
        proficiency_level: int,
        score: float,
        confidence: float,
        verified: bool = False,
        last_assessed_at: datetime | None = None,
    ):
        capability = await self.capability_repository.get_by_id(
            capability_id
        )

        if not capability:
            raise ValueError(
                "Capability does not exist."
            )

        existing = await self.repository.get_user_capability(
            user_id=user_id,
            capability_id=capability_id,
        )

        if existing:
            raise ValueError(
                "User already has this capability."
            )

        return await self.repository.create(
            user_id=user_id,
            capability_id=capability_id,
            proficiency_level=proficiency_level,
            score=score,
            confidence=confidence,
            verified=verified,
            last_assessed_at=last_assessed_at,
        )

    async def update(
        self,
        user_id: str,
        capability_id: str,
        proficiency_level: int | None = None,
        score: float | None = None,
        confidence: float | None = None,
        verified: bool | None = None,
        last_assessed_at: datetime | None = None,
    ):
        capability = await self.capability_repository.get_by_id(
            capability_id
        )

        if not capability:
            raise ValueError(
                "Capability does not exist."
            )

        existing = await self.repository.get_user_capability(
            user_id=user_id,
            capability_id=capability_id,
        )

        if not existing:
            raise ValueError(
                "User does not have this capability."
            )

        return await self.repository.update(
            user_capability=existing,
            proficiency_level=proficiency_level,
            score=score,
            confidence=confidence,
            verified=verified,
            last_assessed_at=last_assessed_at,
        )

    async def create_or_update(
        self,
        user_id: str,
        capability_id: str,
        proficiency_level: int,
        score: float,
        confidence: float,
        verified: bool = False,
        last_assessed_at: datetime | None = None,
    ):
        capability = await self.capability_repository.get_by_id(
            capability_id
        )

        if not capability:
            raise ValueError(
                "Capability does not exist."
            )

        return await self.repository.create_or_update(
            user_id=user_id,
            capability_id=capability_id,
            proficiency_level=proficiency_level,
            score=score,
            confidence=confidence,
            verified=verified,
            last_assessed_at=last_assessed_at,
        )
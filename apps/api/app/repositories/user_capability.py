from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_capability import UserCapability


class UserCapabilityRepository:
    """
    Repository for the current capability state of a user.

    UserCapability represents the latest measured capability state.
    Historical capability measurements are stored separately in
    CapabilityScoreHistory.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        user_capability_id: str,
    ) -> UserCapability | None:
        result = await self.session.execute(
            select(UserCapability).where(
                UserCapability.id == user_capability_id
            )
        )

        return result.scalar_one_or_none()

    async def get_user_capabilities(
        self,
        user_id: str,
    ) -> list[UserCapability]:
        result = await self.session.execute(
            select(UserCapability)
            .where(
                UserCapability.user_id == user_id
            )
            .order_by(UserCapability.created_at)
        )

        return list(result.scalars().all())

    async def get_user_capability(
        self,
        user_id: str,
        capability_id: str,
    ) -> UserCapability | None:
        result = await self.session.execute(
            select(UserCapability).where(
                UserCapability.user_id == user_id,
                UserCapability.capability_id == capability_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: str,
        capability_id: str,
        proficiency_level: int,
        score: float,
        confidence: float,
        verified: bool = False,
        last_assessed_at: datetime | None = None,
    ) -> UserCapability:
        user_capability = UserCapability(
            user_id=user_id,
            capability_id=capability_id,
            proficiency_level=proficiency_level,
            score=score,
            confidence=confidence,
            verified=verified,
            last_assessed_at=last_assessed_at,
        )

        self.session.add(user_capability)

        await self.session.commit()
        await self.session.refresh(user_capability)

        return user_capability

    async def update(
        self,
        user_capability: UserCapability,
        proficiency_level: int | None = None,
        score: float | None = None,
        confidence: float | None = None,
        verified: bool | None = None,
        last_assessed_at: datetime | None = None,
    ) -> UserCapability:
        if proficiency_level is not None:
            user_capability.proficiency_level = proficiency_level

        if score is not None:
            user_capability.score = score

        if confidence is not None:
            user_capability.confidence = confidence

        if verified is not None:
            user_capability.verified = verified

        if last_assessed_at is not None:
            user_capability.last_assessed_at = last_assessed_at

        await self.session.commit()
        await self.session.refresh(user_capability)

        return user_capability

    async def create_or_update(
        self,
        user_id: str,
        capability_id: str,
        proficiency_level: int,
        score: float,
        confidence: float,
        verified: bool = False,
        last_assessed_at: datetime | None = None,
    ) -> UserCapability:
        existing = await self.get_user_capability(
            user_id=user_id,
            capability_id=capability_id,
        )

        if existing is not None:
            return await self.update(
                user_capability=existing,
                proficiency_level=proficiency_level,
                score=score,
                confidence=confidence,
                verified=verified,
                last_assessed_at=last_assessed_at,
            )

        return await self.create(
            user_id=user_id,
            capability_id=capability_id,
            proficiency_level=proficiency_level,
            score=score,
            confidence=confidence,
            verified=verified,
            last_assessed_at=last_assessed_at,
        )
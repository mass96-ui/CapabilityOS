from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capability_score_history import CapabilityScoreHistory


class CapabilityScoreHistoryRepository:
    """
    Repository for longitudinal capability measurements.

    This repository is responsible only for persistence and retrieval
    of capability score history.

    Capability scoring and aggregation logic belong to the
    Capability Scoring Service.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        history_id: str,
    ) -> CapabilityScoreHistory | None:
        result = await self.session.execute(
            select(CapabilityScoreHistory).where(
                CapabilityScoreHistory.id == history_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: str,
    ) -> list[CapabilityScoreHistory]:
        result = await self.session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.user_id == user_id
            )
            .order_by(CapabilityScoreHistory.created_at)
        )

        return list(result.scalars().all())

    async def get_by_capability(
        self,
        capability_id: str,
    ) -> list[CapabilityScoreHistory]:
        result = await self.session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.capability_id == capability_id
            )
            .order_by(CapabilityScoreHistory.created_at)
        )

        return list(result.scalars().all())

    async def get_user_capability_history(
        self,
        user_id: str,
        capability_id: str,
    ) -> list[CapabilityScoreHistory]:
        result = await self.session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.user_id == user_id,
                CapabilityScoreHistory.capability_id == capability_id,
            )
            .order_by(CapabilityScoreHistory.created_at)
        )

        return list(result.scalars().all())

    async def get_latest_user_capability_history(
        self,
        user_id: str,
        capability_id: str,
    ) -> CapabilityScoreHistory | None:
        result = await self.session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.user_id == user_id,
                CapabilityScoreHistory.capability_id == capability_id,
            )
            .order_by(
                CapabilityScoreHistory.created_at.desc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_by_attempt(
        self,
        attempt_id: str,
    ) -> list[CapabilityScoreHistory]:
        result = await self.session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.attempt_id == attempt_id
            )
            .order_by(CapabilityScoreHistory.created_at)
        )

        return list(result.scalars().all())

    async def get_by_evidence(
        self,
        evidence_id: str,
    ) -> list[CapabilityScoreHistory]:
        result = await self.session.execute(
            select(CapabilityScoreHistory)
            .where(
                CapabilityScoreHistory.evidence_id == evidence_id
            )
            .order_by(CapabilityScoreHistory.created_at)
        )

        return list(result.scalars().all())

    async def create(
        self,
        user_id: str,
        capability_id: str,
        score: float,
        proficiency: str | None = None,
        confidence: float = 0.0,
        previous_score: float | None = None,
        score_delta: float | None = None,
        source: str = "assessment",
        attempt_id: str | None = None,
        evidence_id: str | None = None,
        reason: str | None = None,
        metadata_json: str | None = None,
    ) -> CapabilityScoreHistory:
        history = CapabilityScoreHistory(
            user_id=user_id,
            capability_id=capability_id,
            attempt_id=attempt_id,
            evidence_id=evidence_id,
            score=score,
            proficiency=proficiency,
            confidence=confidence,
            previous_score=previous_score,
            score_delta=score_delta,
            source=source,
            reason=reason,
            metadata_json=metadata_json,
        )

        self.session.add(history)

        await self.session.commit()
        await self.session.refresh(history)

        return history
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.capability_score_history import (
    CapabilityScoreHistoryRepository,
)


class CapabilityScoreHistoryService:
    """
    Service for retrieving longitudinal capability score history.

    Business/scoring logic remains in the capability evaluation/scoring
    services. This service only coordinates history retrieval.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = CapabilityScoreHistoryRepository(session)

    async def get_by_id(
        self,
        history_id: str,
    ):
        return await self.repository.get_by_id(history_id)

    async def get_by_user(
        self,
        user_id: str,
    ):
        return await self.repository.get_by_user(user_id)

    async def get_by_capability(
        self,
        capability_id: str,
    ):
        return await self.repository.get_by_capability(capability_id)

    async def get_user_capability_history(
        self,
        user_id: str,
        capability_id: str,
    ):
        return await self.repository.get_user_capability_history(
            user_id,
            capability_id,
        )

    async def get_latest_user_capability_history(
        self,
        user_id: str,
        capability_id: str,
    ):
        return await self.repository.get_latest_user_capability_history(
            user_id,
            capability_id,
        )

    async def get_by_attempt(
        self,
        attempt_id: str,
    ):
        return await self.repository.get_by_attempt(attempt_id)

    async def get_by_evidence(
        self,
        evidence_id: str,
    ):
        return await self.repository.get_by_evidence(evidence_id)

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_evidence import AssessmentEvidence


class AssessmentEvidenceRepository:
    """
    Repository for normalized assessment evidence.

    This repository is responsible only for persistence and retrieval
    of evidence. Capability scoring and aggregation belong to the
    Capability Scoring Service.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        evidence_id: str,
    ) -> AssessmentEvidence | None:

        result = await self.session.execute(
            select(AssessmentEvidence).where(
                AssessmentEvidence.id == evidence_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_attempt(
        self,
        attempt_id: str,
    ) -> list[AssessmentEvidence]:

        result = await self.session.execute(
            select(AssessmentEvidence)
            .where(
                AssessmentEvidence.attempt_id == attempt_id
            )
            .order_by(AssessmentEvidence.created_at)
        )

        return list(result.scalars().all())

    async def get_by_answer(
        self,
        answer_id: str,
    ) -> list[AssessmentEvidence]:

        result = await self.session.execute(
            select(AssessmentEvidence)
            .where(
                AssessmentEvidence.answer_id == answer_id
            )
            .order_by(AssessmentEvidence.created_at)
        )

        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: str,
    ) -> list[AssessmentEvidence]:

        result = await self.session.execute(
            select(AssessmentEvidence)
            .where(
                AssessmentEvidence.user_id == user_id
            )
            .order_by(AssessmentEvidence.created_at)
        )

        return list(result.scalars().all())

    async def get_by_capability(
        self,
        capability_id: str,
    ) -> list[AssessmentEvidence]:

        result = await self.session.execute(
            select(AssessmentEvidence)
            .where(
                AssessmentEvidence.capability_id == capability_id
            )
            .order_by(AssessmentEvidence.created_at)
        )

        return list(result.scalars().all())

    async def get_user_capability_evidence(
        self,
        user_id: str,
        capability_id: str,
    ) -> list[AssessmentEvidence]:

        result = await self.session.execute(
            select(AssessmentEvidence)
            .where(
                AssessmentEvidence.user_id == user_id,
                AssessmentEvidence.capability_id == capability_id,
            )
            .order_by(AssessmentEvidence.created_at)
        )

        return list(result.scalars().all())

    async def create(
        self,
        attempt_id: str,
        answer_id: str,
        user_id: str,
        capability_id: str,
        evidence_score: float,
        evidence_weight: float = 1.0,
        confidence: float = 0.0,
        skill_dimension: str | None = None,
        evidence_type: str = "assessment",
        evaluator_type: str = "rule_based",
        evaluation_reason: str | None = None,
        metadata_json: str | None = None,
    ) -> AssessmentEvidence:

        evidence = AssessmentEvidence(
            attempt_id=attempt_id,
            answer_id=answer_id,
            user_id=user_id,
            capability_id=capability_id,
            skill_dimension=skill_dimension,
            evidence_type=evidence_type,
            evidence_score=evidence_score,
            evidence_weight=evidence_weight,
            confidence=confidence,
            evaluator_type=evaluator_type,
            evaluation_reason=evaluation_reason,
            metadata_json=metadata_json,
        )

        self.session.add(evidence)

        await self.session.commit()
        await self.session.refresh(evidence)

        return evidence
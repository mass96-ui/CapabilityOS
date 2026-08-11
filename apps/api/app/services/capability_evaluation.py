from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.capability_score_history import (
    CapabilityScoreHistoryRepository,
)
from app.repositories.user_capability import (
    UserCapabilityRepository,
)
from app.services.capability_scoring import (
    CapabilityScoreResult,
    CapabilityScoringService,
)
from app.services.proficiency_policy import (
    ProficiencyPolicy,
    ProficiencyPolicyResult,
)


@dataclass(frozen=True)
class CapabilityEstimate:
    """
    Current capability estimate produced by combining:

        1. Evidence measurement
        2. Proficiency interpretation policy

    Measurement tells us what the accumulated evidence supports.

    Policy tells us how that measurement should be interpreted.
    """

    user_id: str
    capability_id: str
    score: float
    confidence: float
    evidence_count: int
    proficiency: str
    proficiency_level: int
    scoring_policy: str
    scoring_policy_version: str


class CapabilityEvaluationService:
    """
    Coordinates capability measurement, proficiency interpretation,
    and persistence.

    Flow:

        Assessment Evidence
                ↓
        CapabilityScoringService
                ↓
        CapabilityScoreResult
                ↓
        ProficiencyPolicy
                ↓
        CapabilityEstimate
                ↓
        UserCapability
                +
        CapabilityScoreHistory
    """

    def __init__(self, session: AsyncSession) -> None:
        self.scoring_service = CapabilityScoringService(session)

        self.proficiency_policy = ProficiencyPolicy()

        self.user_capability_repository = UserCapabilityRepository(
            session
        )

        self.history_repository = CapabilityScoreHistoryRepository(
            session
        )

    async def evaluate_capability(
        self,
        user_id: str,
        capability_id: str,
        attempt_id: str | None = None,
        evidence_id: str | None = None,
        source: str = "assessment",
        reason: str | None = None,
        metadata_json: str | None = None,
        verified: bool = False,
    ) -> CapabilityEstimate:
        """
        Evaluate a user's capability from accumulated evidence.

        The process is deliberately separated:

        1. Measure evidence.
        2. Apply proficiency policy.
        3. Build a capability estimate.
        4. Persist current capability.
        5. Preserve historical interpretation.
        """

        # --------------------------------------------------
        # 1. Measure accumulated evidence
        # --------------------------------------------------

        measurement: CapabilityScoreResult = (
            await self.scoring_service.calculate_capability(
                user_id=user_id,
                capability_id=capability_id,
            )
        )

        # --------------------------------------------------
        # 2. Interpret measurement using policy
        # --------------------------------------------------

        policy_result: ProficiencyPolicyResult = (
            self.proficiency_policy.interpret(
                score=measurement.score,
                confidence=measurement.confidence,
            )
        )

        # --------------------------------------------------
        # 3. Build capability estimate
        # --------------------------------------------------

        estimate = CapabilityEstimate(
            user_id=measurement.user_id,
            capability_id=measurement.capability_id,
            score=measurement.score,
            confidence=measurement.confidence,
            evidence_count=measurement.evidence_count,
            proficiency=policy_result.proficiency,
            proficiency_level=policy_result.proficiency_level,
            scoring_policy=self.proficiency_policy.name,
            scoring_policy_version=self.proficiency_policy.version,
        )

        # --------------------------------------------------
        # 4. Get previous capability state
        # --------------------------------------------------

        existing = (
            await self.user_capability_repository
            .get_user_capability(
                user_id=user_id,
                capability_id=capability_id,
            )
        )

        previous_score = (
            existing.score
            if existing is not None
            else None
        )

        score_delta = (
            estimate.score - previous_score
            if previous_score is not None
            else None
        )

        now = datetime.now(timezone.utc)

        # --------------------------------------------------
        # 5. Persist current capability state
        # --------------------------------------------------

        await self.user_capability_repository.create_or_update(
            user_id=user_id,
            capability_id=capability_id,
            proficiency_level=estimate.proficiency_level,
            score=estimate.score,
            confidence=estimate.confidence,
            verified=verified,
            last_assessed_at=now,
        )

        # --------------------------------------------------
        # 6. Preserve historical interpretation
        # --------------------------------------------------

        await self.history_repository.create(
            user_id=user_id,
            capability_id=capability_id,
            score=estimate.score,
            proficiency=estimate.proficiency,
            confidence=estimate.confidence,
            previous_score=previous_score,
            score_delta=score_delta,
            source=source,
            attempt_id=attempt_id,
            evidence_id=evidence_id,
            reason=reason,
            metadata_json=metadata_json,
        )

        return estimate
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.assessment_evidence import (
    AssessmentEvidenceRepository,
)


@dataclass(frozen=True)
class CapabilityScoreResult:
    """
    Calculated capability estimate produced from accumulated evidence.

    This is a measurement result, not the user's persisted capability
    state. UserCapability remains responsible for the current/latest
    capability representation.
    """

    user_id: str
    capability_id: str
    score: float
    proficiency: str
    proficiency_level: int
    confidence: float
    evidence_count: int

    # Evidence intelligence
    effective_evidence_weight: float
    evidence_quality: float
    recency_factor: float
    consistency: float


class CapabilityScoringService:
    """
    Capability Intelligence scoring service.

    Evidence is transformed into effective weights using:

        base_weight
        Ã— recency
        Ã— quality
        Ã— confidence

    This is the first evolution beyond a simple weighted average.

    The algorithm is intentionally deterministic and explainable.
    """

    # ---------------------------------------------------------
    # Evidence intelligence configuration
    # ---------------------------------------------------------

    RECENCY_HALF_LIFE_DAYS = 180.0

    MIN_RECENCY_FACTOR = 0.25

    MIN_QUALITY_FACTOR = 0.50

    def __init__(self, session: AsyncSession) -> None:
        self.evidence_repository = AssessmentEvidenceRepository(
            session
        )

    # =========================================================
    # Main calculation
    # =========================================================

    async def calculate_capability(
        self,
        user_id: str,
        capability_id: str,
    ) -> CapabilityScoreResult:
        """
        Calculate a capability estimate from accumulated evidence.

        Each evidence item receives an effective weight:

            effective_weight =
                evidence_weight
                Ã— recency_factor
                Ã— quality_factor
                Ã— confidence_factor

        The final score is normalized to 0-100.
        Confidence is normalized to 0-1.
        """

        evidence = (
            await self.evidence_repository
            .get_user_capability_evidence(
                user_id=user_id,
                capability_id=capability_id,
            )
        )

        if not evidence:
            raise ValueError(
                "No capability evidence exists for this user."
            )

        weighted_score = 0.0
        weighted_confidence = 0.0
        total_effective_weight = 0.0

        quality_values: list[float] = []
        recency_values: list[float] = []
        score_values: list[float] = []

        now = datetime.now(timezone.utc)

        for item in evidence:
            base_weight = max(
                float(item.evidence_weight),
                0.0,
            )

            if base_weight <= 0:
                continue

            evidence_confidence = self._normalize_confidence(
                float(item.confidence)
            )

            recency_factor = self._calculate_recency_factor(
                item.created_at,
                now,
            )

            quality_factor = self._calculate_quality_factor(
                evaluator_type=item.evaluator_type,
                evidence_type=item.evidence_type,
                confidence=evidence_confidence,
            )

            effective_weight = (
                base_weight
                * recency_factor
                * quality_factor
                * self._confidence_weight(
                    evidence_confidence
                )
            )

            if effective_weight <= 0:
                continue

            evidence_score = self._normalize_score(
                float(item.evidence_score)
            )

            weighted_score += (
                evidence_score * effective_weight
            )

            weighted_confidence += (
                evidence_confidence * effective_weight
            )

            total_effective_weight += effective_weight

            quality_values.append(quality_factor)
            recency_values.append(recency_factor)
            score_values.append(evidence_score)

        if total_effective_weight <= 0:
            raise ValueError(
                "Capability evidence has no usable weight."
            )

        score = (
            weighted_score
            / total_effective_weight
        )

        confidence = (
            weighted_confidence
            / total_effective_weight
        )

        evidence_quality = (
            sum(quality_values)
            / len(quality_values)
            if quality_values
            else 0.0
        )

        recency_factor = (
            sum(recency_values)
            / len(recency_values)
            if recency_values
            else 0.0
        )

        consistency = self._calculate_consistency(
            score_values
        )

        score = self._normalize_score(score)

        confidence = self._normalize_confidence(
            confidence
        )

        proficiency = self._determine_proficiency(
            score=score,
            confidence=confidence,
        )

        proficiency_level = self._proficiency_to_level(
            proficiency
        )

        return CapabilityScoreResult(
            user_id=user_id,
            capability_id=capability_id,
            score=score,
            proficiency=proficiency,
            proficiency_level=proficiency_level,
            confidence=confidence,
            evidence_count=len(evidence),
            effective_evidence_weight=(
                total_effective_weight
            ),
            evidence_quality=evidence_quality,
            recency_factor=recency_factor,
            consistency=consistency,
        )

    # =========================================================
    # Recency intelligence
    # =========================================================

    @classmethod
    def _calculate_recency_factor(
        cls,
        created_at: datetime,
        now: datetime,
    ) -> float:
        """
        Calculate how relevant evidence is based on age.

        Uses exponential decay with a 180-day half-life.

        Recent evidence approaches 1.0.

        Older evidence gradually loses influence but never
        completely disappears.
        """

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        age_seconds = max(
            (now - created_at).total_seconds(),
            0.0,
        )

        age_days = age_seconds / 86400.0

        decay = exp(
            -0.69314718056
            * age_days
            / cls.RECENCY_HALF_LIFE_DAYS
        )

        return max(
            cls.MIN_RECENCY_FACTOR,
            min(decay, 1.0),
        )

    # =========================================================
    # Evidence quality
    # =========================================================

    @classmethod
    def _calculate_quality_factor(
        cls,
        *,
        evaluator_type: str | None,
        evidence_type: str | None,
        confidence: float,
    ) -> float:
        """
        Estimate evidence reliability.

        This is deliberately conservative in v1.

        Higher-confidence and stronger evidence sources receive
        greater influence.

        Future versions can replace this with a configurable
        evidence reliability registry.
        """

        evaluator_quality = {
            "rule_based": 0.80,
            "human": 1.00,
            "expert": 1.00,
            "ai": 0.75,
            "llm": 0.75,
        }

        evidence_quality = {
            "assessment": 0.80,
            "project": 1.00,
            "task": 0.95,
            "interview": 1.00,
            "self_reported": 0.50,
        }

        evaluator_factor = evaluator_quality.get(
            (evaluator_type or "").lower(),
            0.70,
        )

        type_factor = evidence_quality.get(
            (evidence_type or "").lower(),
            0.70,
        )

        confidence_factor = (
            0.50
            + (0.50 * confidence)
        )

        quality = (
            evaluator_factor
            * type_factor
            * confidence_factor
        )

        return max(
            cls.MIN_QUALITY_FACTOR,
            min(quality, 1.0),
        )

    # =========================================================
    # Confidence weighting
    # =========================================================

    @staticmethod
    def _confidence_weight(
        confidence: float,
    ) -> float:
        """
        Convert confidence into a weighting multiplier.

        A confidence of 1.0 produces full influence.

        A confidence of 0.0 still retains limited influence,
        preventing a single uncertain evidence item from being
        completely discarded.
        """

        return 0.50 + (
            0.50 * confidence
        )

    # =========================================================
    # Consistency
    # =========================================================

    @staticmethod
    def _calculate_consistency(
        scores: list[float],
    ) -> float:
        """
        Estimate consistency of observed performance.

        1.0 = highly consistent
        0.0 = highly inconsistent

        Uses mean absolute deviation from the mean.
        """

        if len(scores) <= 1:
            return 1.0

        mean_score = (
            sum(scores)
            / len(scores)
        )

        mean_deviation = (
            sum(
                abs(score - mean_score)
                for score in scores
            )
            / len(scores)
        )

        consistency = 1.0 - (
            mean_deviation / 50.0
        )

        return max(
            0.0,
            min(consistency, 1.0),
        )

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _normalize_score(
        score: float,
    ) -> float:
        """
        Normalize capability score to 0-100.
        """

        return max(
            0.0,
            min(float(score), 100.0),
        )

    @staticmethod
    def _normalize_confidence(
        confidence: float,
    ) -> float:
        """
        Normalize confidence to 0-1.
        """

        return max(
            0.0,
            min(float(confidence), 1.0),
        )

    # =========================================================
    # Proficiency
    # =========================================================

    @staticmethod
    def _determine_proficiency(
        score: float,
        confidence: float,
    ) -> str:
        """
        Determine current proficiency estimate.

        Proficiency depends on both capability score and
        confidence.
        """

        if confidence < 0.30:
            return "emerging"

        if score < 40.0:
            return "emerging"

        if score < 60.0:
            return "developing"

        if score < 80.0:
            return "proficient"

        return "advanced"

    @staticmethod
    def _proficiency_to_level(
        proficiency: str,
    ) -> int:
        """
        Convert proficiency state into its integer level.

        emerging   = 1
        developing = 2
        proficient = 3
        advanced   = 4
        """

        levels = {
            "emerging": 1,
            "developing": 2,
            "proficient": 3,
            "advanced": 4,
        }

        return levels.get(
            proficiency,
            1,
        )

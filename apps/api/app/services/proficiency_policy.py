from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProficiencyPolicyResult:
    """
    Result produced by a proficiency interpretation policy.
    """

    proficiency: str
    proficiency_level: int


class ProficiencyPolicy:
    """
    MVP proficiency interpretation policy.

    This policy interprets an already-calculated capability
    measurement.

    Policy v1 preserves the existing CapabilityOS behavior:

        confidence < 0.30 -> emerging
        score < 40        -> emerging
        score < 60        -> developing
        score < 80        -> proficient
        score >= 80       -> advanced

    These thresholds are policy behavior, not universal
    capability truth.
    """

    name = "mvp_threshold"
    version = "1"

    def interpret(
        self,
        *,
        score: float,
        confidence: float,
    ) -> ProficiencyPolicyResult:
        if confidence < 0.30:
            proficiency = "emerging"
        elif score < 40.0:
            proficiency = "emerging"
        elif score < 60.0:
            proficiency = "developing"
        elif score < 80.0:
            proficiency = "proficient"
        else:
            proficiency = "advanced"

        levels = {
            "emerging": 1,
            "developing": 2,
            "proficient": 3,
            "advanced": 4,
        }

        return ProficiencyPolicyResult(
            proficiency=proficiency,
            proficiency_level=levels[proficiency],
        )
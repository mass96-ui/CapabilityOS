from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RequirementMatch:
    requirement_id: str
    capability_id: str
    required_level: int
    current_level: int | None
    importance: float
    required: bool
    status: str
    gap: int


@dataclass(frozen=True)
class ProjectMatchResult:
    eligible: bool
    match_score: float
    matched: List[RequirementMatch]
    gaps: List[RequirementMatch]
    missing: List[RequirementMatch]


class ProjectMatchingService:
    """Deterministic project-to-user capability matching."""

    @staticmethod
    def evaluate(
        requirements,
        user_capabilities_by_capability_id,
    ) -> ProjectMatchResult:
        matched = []
        gaps = []
        missing = []

        total_weight = 0.0
        achieved_weight = 0.0

        for requirement in requirements:
            weight = max(float(requirement.importance), 0.0)
            total_weight += weight

            capability = user_capabilities_by_capability_id.get(
                requirement.capability_id
            )

            if capability is None:
                item = RequirementMatch(
                    requirement_id=requirement.id,
                    capability_id=requirement.capability_id,
                    required_level=requirement.minimum_proficiency_level,
                    current_level=None,
                    importance=weight,
                    required=requirement.required,
                    status="missing",
                    gap=requirement.minimum_proficiency_level,
                )
                missing.append(item)
                continue

            current_level = int(capability.proficiency_level)
            required_level = int(requirement.minimum_proficiency_level)
            gap = max(required_level - current_level, 0)

            if gap == 0:
                status = "matched"
                achieved_weight += weight
                target = matched
            else:
                status = "gap"
                achieved_weight += weight * min(
                    current_level / required_level, 1.0
                )
                target = gaps

            target.append(
                RequirementMatch(
                    requirement_id=requirement.id,
                    capability_id=requirement.capability_id,
                    required_level=required_level,
                    current_level=current_level,
                    importance=weight,
                    required=requirement.required,
                    status=status,
                    gap=gap,
                )
            )

        match_score = (
            round((achieved_weight / total_weight) * 100, 2)
            if total_weight
            else 100.0
        )

        required_missing = any(item.required for item in missing)
        required_gaps = any(item.required for item in gaps)

        return ProjectMatchResult(
            eligible=not required_missing and not required_gaps,
            match_score=match_score,
            matched=matched,
            gaps=gaps,
            missing=missing,
        )

from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment
from app.models.assessment_attempt import AssessmentAttempt
from app.models.capability import Capability
from app.models.capability_score_history import CapabilityScoreHistory
from app.models.project import Project
from app.models.user import User
from app.models.user_capability import UserCapability
from app.repositories.assessment_attempt import (
    AssessmentAttemptRepository,
)
from app.repositories.assessment_evidence import (
    AssessmentEvidenceRepository,
)
from app.repositories.capability import CapabilityRepository
from app.repositories.capability_score_history import (
    CapabilityScoreHistoryRepository,
)
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.repositories.user_capability import (
    UserCapabilityRepository,
)
from app.schemas.passport import (
    EngineeringPassport,
    PassportAssessmentHistoryItem,
    PassportCapability,
    PassportCapabilityHistoryItem,
    PassportProjectExperience,
    PassportProfile,
)


class EngineeringPassportService:
    """
    Aggregates authoritative platform data into an Engineering Passport.

    The passport is a read-only projection over existing data:

    - User + LearnerProfile
    - UserCapability + Capability
    - CapabilityScoreHistory
    - AssessmentAttempt + Assessment
    - Project ownership

    No duplicate scoring. No new business logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.capability_repository = CapabilityRepository(session)
        self.user_capability_repository = UserCapabilityRepository(session)
        self.history_repository = CapabilityScoreHistoryRepository(session)
        self.attempt_repository = AssessmentAttemptRepository(session)
        self.project_repository = ProjectRepository(session)

    async def build_passport(
        self,
        user_id: str,
    ) -> EngineeringPassport:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        capabilities = (
            await self.user_capability_repository.get_user_capabilities(
                user_id=user_id
            )
        )

        capability_map = {
            cap.capability_id: cap for cap in capabilities
        }

        capability_ids = list(capability_map.keys())

        capability_details: dict[str, Capability] = {}

        if capability_ids:
            for capability_id in capability_ids:
                capability = (
                    await self.capability_repository.get_by_id(
                        capability_id
                    )
                )

                if capability is not None:
                    capability_details[capability_id] = capability

        history_items = (
            await self.history_repository.get_by_user(user_id)
        )

        attempts = (
            await self.attempt_repository.get_by_user(
                user_id=user_id
            )
        )

        assessment_ids = list(
            {
                attempt.assessment_id
                for attempt in attempts
            }
        )

        assessment_map: dict[str, Assessment] = {}

        for assessment_id in assessment_ids:
            assessment = (
                await self.session.get(Assessment, assessment_id)
            )

            if assessment is not None:
                assessment_map[assessment_id] = assessment

        projects = (
            await self.project_repository.get_by_owner(
                owner_id=user_id
            )
        )

        passport_capabilities: list[PassportCapability] = []

        for user_cap in capabilities:
            capability = capability_details.get(
                user_cap.capability_id
            )

            if capability is None:
                continue

            passport_capabilities.append(
                PassportCapability(
                    id=capability.id,
                    name=capability.name,
                    slug=capability.slug,
                    category=capability.category,
                    proficiency_level=user_cap.proficiency_level,
                    score=user_cap.score,
                    confidence=user_cap.confidence,
                    verified=user_cap.verified,
                    last_assessed_at=user_cap.last_assessed_at,
                )
            )

        passport_assessment_history: list[
            PassportAssessmentHistoryItem
        ] = []

        for attempt in attempts:
            assessment = assessment_map.get(
                attempt.assessment_id
            )

            if assessment is None:
                continue

            passport_assessment_history.append(
                PassportAssessmentHistoryItem(
                    attempt_id=attempt.id,
                    assessment_id=attempt.assessment_id,
                    assessment_title=assessment.title,
                    status=attempt.status,
                    score=attempt.score,
                    max_score=attempt.max_score,
                    percentage=attempt.percentage,
                    submitted_at=attempt.submitted_at,
                )
            )

        passport_capability_history: list[
            PassportCapabilityHistoryItem
        ] = []

        for history_item in history_items:
            passport_capability_history.append(
                PassportCapabilityHistoryItem(
                    id=history_item.id,
                    score=history_item.score,
                    proficiency=history_item.proficiency,
                    confidence=history_item.confidence,
                    previous_score=history_item.previous_score,
                    score_delta=history_item.score_delta,
                    source=history_item.source,
                    reason=history_item.reason,
                    created_at=history_item.created_at,
                )
            )

        passport_projects: list[PassportProjectExperience] = []

        for project in projects:
            passport_projects.append(
                PassportProjectExperience(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    status=project.status,
                    project_type=project.project_type,
                    created_at=project.created_at,
                )
            )

        return EngineeringPassport(
            profile=PassportProfile(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_verified=user.is_verified,
            ),
            capabilities=passport_capabilities,
            assessment_history=passport_assessment_history,
            capability_history=passport_capability_history,
            project_experience=passport_projects,
            generated_at=datetime.now(datetime.now().astimezone().tzinfo),
        )

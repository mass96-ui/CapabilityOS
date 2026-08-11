from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learner.profile import LearnerProfile
from app.repositories.learner.profile import LearnerProfileRepository
from app.services.base import BaseService


class LearnerProfileService(BaseService[LearnerProfile]):
    """
    Business logic for learner profiles.

    This service deliberately does not own:
    - authentication
    - capabilities
    - assessments
    - scoring
    - projects

    Those remain independent services.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=LearnerProfile,
        )

        self.profile_repository = LearnerProfileRepository(
            session=session,
        )

    # ==========================================================
    # GET PROFILE
    # ==========================================================

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> LearnerProfile | None:
        return await self.profile_repository.get_by_user_id(
            user_id=user_id,
        )

    # ==========================================================
    # CREATE PROFILE
    # ==========================================================

    async def create_profile(
        self,
        user_id: str,
        display_name: str | None = None,
        headline: str | None = None,
        bio: str | None = None,
        location: str | None = None,
        profile_image_url: str | None = None,
    ) -> LearnerProfile:

        existing = await self.profile_repository.get_by_user_id(
            user_id=user_id,
        )

        if existing is not None:
            raise ValueError(
                "Learner profile already exists for this user."
            )

        profile = LearnerProfile(
            user_id=user_id,
            display_name=display_name,
            headline=headline,
            bio=bio,
            location=location,
            profile_image_url=profile_image_url,
        )

        self.session.add(profile)

        await self.session.flush()
        await self.session.refresh(profile)

        return profile

    # ==========================================================
    # UPDATE PROFILE
    # ==========================================================

    async def update_profile(
        self,
        user_id: str,
        **updates,
    ) -> LearnerProfile | None:

        profile = await self.profile_repository.get_by_user_id(
            user_id=user_id,
        )

        if profile is None:
            return None

        allowed_fields = {
            "display_name",
            "headline",
            "bio",
            "location",
            "profile_image_url",
        }

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(profile, field, value)

        await self.session.flush()
        await self.session.refresh(profile)

        return profile
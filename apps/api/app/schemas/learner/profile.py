from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LearnerProfileBase(BaseModel):
    """
    Base learner profile representation.

    This schema intentionally contains learner identity and
    presentation-level information only.

    Capability scores, assessments, evidence, projects and
    recommendations remain separate bounded modules.
    """

    display_name: str | None = Field(
        default=None,
        max_length=100,
    )

    headline: str | None = Field(
        default=None,
        max_length=160,
    )

    bio: str | None = Field(
        default=None,
        max_length=1000,
    )

    location: str | None = Field(
        default=None,
        max_length=120,
    )

    profile_image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class LearnerProfileCreate(LearnerProfileBase):
    """
    Payload used to create a learner profile.
    """

    user_id: UUID


class LearnerProfileUpdate(BaseModel):
    """
    Partial update payload.

    Every field is optional so learners can update individual
    profile attributes without affecting other modules.
    """

    display_name: str | None = Field(
        default=None,
        max_length=100,
    )

    headline: str | None = Field(
        default=None,
        max_length=160,
    )

    bio: str | None = Field(
        default=None,
        max_length=1000,
    )

    location: str | None = Field(
        default=None,
        max_length=120,
    )

    profile_image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class LearnerProfileResponse(LearnerProfileBase):
    """
    Public/API representation of a learner profile.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
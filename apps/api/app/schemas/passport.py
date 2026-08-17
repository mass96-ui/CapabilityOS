from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PassportCapability(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    category: str
    proficiency_level: int
    score: float
    confidence: float
    verified: bool
    last_assessed_at: datetime | None


class PassportAssessmentHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt_id: str
    assessment_id: str
    assessment_title: str
    status: str
    score: float | None
    max_score: float | None
    percentage: float | None
    submitted_at: datetime | None


class PassportCapabilityHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    score: float
    proficiency: str | None
    confidence: float
    previous_score: float | None
    score_delta: float | None
    source: str
    reason: str | None
    created_at: datetime


class PassportProjectExperience(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: str
    project_type: str
    created_at: datetime


class PassportProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    is_verified: bool
    display_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    location: str | None = None


class EngineeringPassport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile: PassportProfile
    capabilities: list[PassportCapability]
    assessment_history: list[PassportAssessmentHistoryItem]
    capability_history: list[PassportCapabilityHistoryItem]
    project_experience: list[PassportProjectExperience]
    generated_at: datetime

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssessmentAttemptCreate(BaseModel):
    assessment_id: str


class AssessmentAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    assessment_id: str

    status: str

    question_count: int
    answered_count: int
    correct_count: int

    score: float | None
    max_score: float | None
    percentage: float | None

    started_at: datetime
    submitted_at: datetime | None

    created_at: datetime
    updated_at: datetime


class AssessmentAttemptProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    assessment_id: str
    status: str
    started_at: datetime
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AssessmentCapabilityEstimate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    capability_id: str
    score: float
    confidence: float
    evidence_count: int
    proficiency: str
    proficiency_level: int
    scoring_policy: str
    scoring_policy_version: str


class AssessmentAttemptSubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt: AssessmentAttemptResponse
    capability: AssessmentCapabilityEstimate | None
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssessmentAttemptCreate(BaseModel):
    user_id: str
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


class AssessmentAttemptSubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt: AssessmentAttemptResponse
    capability: dict | None
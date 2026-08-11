from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssessmentAnswerCreate(BaseModel):
    attempt_id: str
    question_id: str
    selected_answer: str


class AssessmentAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    attempt_id: str
    question_id: str

    selected_answer: str
    is_correct: bool
    points_earned: int

    answered_at: datetime

    created_at: datetime
    updated_at: datetime

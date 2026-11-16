from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssessmentAnswerCreate(BaseModel):
    attempt_id: str
    question_id: str
    selected_answer: str = Field(min_length=1, max_length=500)

    @field_validator("selected_answer")
    @classmethod
    def selected_answer_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Selected answer must not be blank.")
        return value


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

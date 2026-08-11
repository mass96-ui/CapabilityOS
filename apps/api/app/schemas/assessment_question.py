from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssessmentQuestionCreate(BaseModel):
    assessment_id: str
    question_order: int = Field(default=1, ge=1)
    question_type: str = "mcq"
    question_text: str
    options_json: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    points: int = Field(default=1, ge=1)
    is_active: bool = True


class AssessmentQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str

    question_order: int
    question_type: str
    question_text: str
    options_json: str | None
    correct_answer: str | None
    explanation: str | None

    points: int
    is_active: bool

    created_at: datetime
    updated_at: datetime

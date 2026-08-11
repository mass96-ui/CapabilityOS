from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    capability_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=150)
    slug: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    difficulty: str = Field(default="beginner", max_length=50)
    time_limit_minutes: int | None = Field(default=None, gt=0)
    is_active: bool = True


class AssessmentResponse(BaseModel):
    id: str
    capability_id: str
    title: str
    slug: str
    description: str | None
    difficulty: str
    time_limit_minutes: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserCapabilityCreate(BaseModel):

    capability_id: str

    proficiency_level: int = Field(
        default=1,
        ge=1,
        le=5,
    )

    score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    verified: bool = False


class UserCapabilityResponse(BaseModel):

    id: str
    user_id: str
    capability_id: str
    proficiency_level: int
    score: float
    confidence: float
    verified: bool
    last_assessed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }

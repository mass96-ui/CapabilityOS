from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectRequirementCreate(BaseModel):
    project_id: str

    capability_id: str

    description: str | None = None

    minimum_proficiency_level: int = Field(
        default=1,
        ge=1,
        le=5,
    )

    importance: float = Field(
        default=1.0,
        gt=0,
        le=1,
    )

    required: bool = True


class ProjectRequirementUpdate(BaseModel):
    description: str | None = None

    minimum_proficiency_level: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    importance: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    required: bool | None = None


class ProjectRequirementResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    project_id: str

    capability_id: str

    capability_name: str | None = None

    description: str | None

    minimum_proficiency_level: int

    importance: float

    required: bool

    created_at: datetime

    updated_at: datetime
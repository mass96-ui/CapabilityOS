from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    project_type: str = Field(
        default="real_world",
        max_length=50,
    )

    owner_id: str

    organization_id: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )

    project_type: str | None = Field(
        default=None,
        max_length=50,
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    name: str
    description: str | None

    status: str
    project_type: str

    owner_id: str
    organization_id: str | None

    created_at: datetime
    updated_at: datetime
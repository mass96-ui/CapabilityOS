from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RequirementMatchResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    requirement_id: str
    capability_id: str
    capability_name: Optional[str] = None
    required_level: int
    current_level: Optional[int] = None
    importance: float
    required: bool
    status: str
    gap: int


class ProjectMatchResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    project_id: str
    user_id: str
    eligible: bool
    match_score: float
    coverage_ratio: float
    matched: List[RequirementMatchResponse]
    gaps: List[RequirementMatchResponse]
    missing: List[RequirementMatchResponse]


class CandidateMatchResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: str
    user_email: str
    user_name: str
    eligible: bool
    match_score: float
    coverage_ratio: float
    matched: List[RequirementMatchResponse]
    gaps: List[RequirementMatchResponse]
    missing: List[RequirementMatchResponse]


class ManagerMatchResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    project_id: str
    total_candidates: int
    eligible_count: int
    page: int
    page_size: int
    total_pages: int
    matches: List[CandidateMatchResponse]


class MatchPaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

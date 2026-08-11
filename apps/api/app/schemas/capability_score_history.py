from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CapabilityScoreHistoryResponse(BaseModel):
    id: str
    user_id: str
    capability_id: str
    attempt_id: str | None
    evidence_id: str | None
    score: float
    proficiency: str | None
    confidence: float
    previous_score: float | None
    score_delta: float | None
    source: str
    reason: str | None
    metadata_json: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

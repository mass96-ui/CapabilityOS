from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AssessmentEvidence(Base):
    """
    Normalized evidence extracted from an assessment response.

    One assessment response may produce one or more evidence signals.

    AssessmentEvidence is not the final capability state.
    It represents measurable evidence that can later contribute to
    capability scoring and longitudinal capability history.
    """

    __tablename__ = "assessment_evidence"

    __table_args__ = (
        Index(
            "ix_assessment_evidence_attempt_id",
            "attempt_id",
        ),
        Index(
            "ix_assessment_evidence_answer_id",
            "answer_id",
        ),
        Index(
            "ix_assessment_evidence_capability_id",
            "capability_id",
        ),
        Index(
            "ix_assessment_evidence_user_id",
            "user_id",
        ),
        Index(
            "ix_assessment_evidence_skill_dimension",
            "skill_dimension",
        ),
    )

    # ==========================================================
    # Primary Key
    # ==========================================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # ==========================================================
    # Source / Lineage
    # ==========================================================

    attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_attempts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    answer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_answers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    capability_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "capabilities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Evidence Classification
    # ==========================================================

    skill_dimension: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="assessment",
    )

    # ==========================================================
    # Evidence Measurement
    # ==========================================================

    evidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    evidence_weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # ==========================================================
    # Evaluation Metadata
    # ==========================================================

    evaluator_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="rule_based",
    )

    evaluation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==========================================================
    # Audit
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"AssessmentEvidence("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"capability_id={self.capability_id!r}, "
            f"evidence_score={self.evidence_score!r}, "
            f"confidence={self.confidence!r}"
            f")"
        )
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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CapabilityScoreHistory(Base):
    """
    Historical capability measurements for a user.

    UserCapability represents the current capability state.

    CapabilityScoreHistory preserves the longitudinal history of
    capability score, proficiency and confidence changes.

    This model is append-oriented: each meaningful capability
    evaluation creates a historical record rather than destroying
    the previous measurement.
    """

    __tablename__ = "capability_score_history"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "capability_id",
            "attempt_id",
            name="uq_capability_history_attempt",
        ),
        Index(
            "ix_capability_score_history_user_id",
            "user_id",
        ),
        Index(
            "ix_capability_score_history_capability_id",
            "capability_id",
        ),
        Index(
            "ix_capability_score_history_attempt_id",
            "attempt_id",
        ),
        Index(
            "ix_capability_score_history_evidence_id",
            "evidence_id",
        ),
        Index(
            "ix_capability_score_history_user_capability",
            "user_id",
            "capability_id",
        ),
        Index(
            "ix_capability_score_history_created_at",
            "created_at",
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
    # Identity / Lineage
    # ==========================================================

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

    attempt_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_attempts.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    evidence_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_evidence.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ==========================================================
    # Capability Measurement
    # ==========================================================

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    proficiency: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # ==========================================================
    # Change Information
    # ==========================================================

    previous_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    score_delta: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="assessment",
    )

    reason: Mapped[str | None] = mapped_column(
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

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"CapabilityScoreHistory("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"capability_id={self.capability_id!r}, "
            f"score={self.score!r}, "
            f"proficiency={self.proficiency!r}, "
            f"confidence={self.confidence!r}"
            f")"
        )

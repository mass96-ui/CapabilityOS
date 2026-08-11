from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CapabilityEvaluation(Base):
    """
    Represents an evaluation of a user's capability based on evidence.

    An evaluation is an individual evidence record. It does not represent
    the user's final or aggregated capability state.

    For the initial implementation, the primary evidence source is an
    assessment attempt.
    """

    __tablename__ = "capability_evaluations"

    __table_args__ = (
        UniqueConstraint(
            "assessment_attempt_id",
            "capability_id",
            name="uq_capability_evaluation_attempt_capability",
        ),
        Index(
            "ix_capability_evaluations_user_id",
            "user_id",
        ),
        Index(
            "ix_capability_evaluations_capability_id",
            "capability_id",
        ),
        Index(
            "ix_capability_evaluations_assessment_attempt_id",
            "assessment_attempt_id",
        ),
        Index(
            "ix_capability_evaluations_user_capability",
            "user_id",
            "capability_id",
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
    # Evaluation Context
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

    assessment_attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_attempts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Capability Evaluation
    # ==========================================================

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    proficiency_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    evaluation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="assessment",
    )

    # ==========================================================
    # Evaluation Audit
    # ==========================================================

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

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

    def __repr__(self) -> str:
        return (
            f"CapabilityEvaluation("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"capability_id={self.capability_id!r}, "
            f"assessment_attempt_id={self.assessment_attempt_id!r}, "
            f"score={self.score!r}"
            f")"
        )
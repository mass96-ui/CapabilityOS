from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Float,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AssessmentAttempt(Base):
    """
    Represents one user's attempt at an assessment.

    An Assessment is reusable.
    An AssessmentAttempt belongs to one user and one assessment.
    """

    __tablename__ = "assessment_attempts"

    __table_args__ = (
        Index(
            "ix_assessment_attempts_user_id",
            "user_id",
        ),
        Index(
            "ix_assessment_attempts_assessment_id",
            "assessment_id",
        ),
        Index(
            "ix_assessment_attempts_status",
            "status",
        ),
        Index(
            "ix_assessment_attempts_user_assessment",
            "user_id",
            "assessment_id",
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
    # Relationships
    # ==========================================================

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Attempt State
    # ==========================================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="in_progress",
    )

    # ==========================================================
    # Assessment Statistics
    # ==========================================================

    question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    answered_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    correct_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    max_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ==========================================================
    # Timing
    # ==========================================================

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    def __repr__(self) -> str:
        return (
            f"AssessmentAttempt("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"assessment_id={self.assessment_id!r}, "
            f"status={self.status!r}"
            f")"
        )

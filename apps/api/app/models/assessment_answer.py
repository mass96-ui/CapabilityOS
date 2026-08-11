from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AssessmentAnswer(Base):
    """
    Represents one user's answer to one assessment question.

    An answer belongs to an assessment attempt and a question.
    """

    __tablename__ = "assessment_answers"

    __table_args__ = (
        Index(
            "ix_assessment_answers_attempt_id",
            "attempt_id",
        ),
        Index(
            "ix_assessment_answers_question_id",
            "question_id",
        ),
        Index(
            "ix_assessment_answers_attempt_question",
            "attempt_id",
            "question_id",
            unique=True,
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

    attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_attempts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessment_questions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Answer
    # ==========================================================

    selected_answer: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    points_earned: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # ==========================================================
    # Timing
    # ==========================================================

    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
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
            f"AssessmentAnswer("
            f"id={self.id!r}, "
            f"attempt_id={self.attempt_id!r}, "
            f"question_id={self.question_id!r}, "
            f"is_correct={self.is_correct!r}"
            f")"
        )

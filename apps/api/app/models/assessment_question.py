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
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AssessmentQuestion(Base):
    """
    Represents one question belonging to an assessment.

    Questions are reusable definitions attached to an Assessment.
    """

    __tablename__ = "assessment_questions"

    __table_args__ = (
        Index(
            "ix_assessment_questions_assessment_id",
            "assessment_id",
        ),
        Index(
            "ix_assessment_questions_order",
            "assessment_id",
            "question_order",
        ),
        Index(
            "ix_assessment_questions_is_active",
            "is_active",
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
    # Assessment
    # ==========================================================

    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assessments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Question Information
    # ==========================================================

    question_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    question_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="mcq",
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # JSON string for choices/options.
    # Example:
    # ["A","B","C","D"]
    options_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Correct answer stored separately so scoring
    # can remain deterministic.
    correct_answer: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
            f"AssessmentQuestion("
            f"id={self.id!r}, "
            f"assessment_id={self.assessment_id!r}, "
            f"question_order={self.question_order!r}"
            f")"
        )

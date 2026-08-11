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


class Assessment(Base):
    """
    Assessment definition used to evaluate a user's capability.
    """

    __tablename__ = "assessments"

    __table_args__ = (
        Index(
            "ix_assessments_capability_id",
            "capability_id",
        ),
        Index(
            "ix_assessments_slug",
            "slug",
        ),
        Index(
            "ix_assessments_difficulty",
            "difficulty",
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
    # Capability
    # ==========================================================

    capability_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "capabilities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Assessment Information
    # ==========================================================

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="beginner",
    )

    time_limit_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
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
            f"Assessment("
            f"id={self.id!r}, "
            f"title={self.title!r}, "
            f"capability_id={self.capability_id!r}"
            f")"
        )

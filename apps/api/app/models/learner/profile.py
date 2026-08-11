from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LearnerProfile(Base):
    """
    Learner Profile Model.

    This model contains learner-specific profile information.
    Authentication and core identity remain owned by the User model.

    Design principle:
    - User owns authentication/identity.
    - LearnerProfile owns learner presentation/profile information.
    - Capabilities, assessments, evidence and projects remain separate
      bounded domains.
    """

    __tablename__ = "learner_profiles"

    __table_args__ = (
        Index("ix_learner_profiles_user_id", "user_id"),
    )

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # ==========================================================
    # USER REFERENCE
    # ==========================================================

    user_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
    )

    # ==========================================================
    # PROFILE INFORMATION
    # ==========================================================

    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    headline: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    profile_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ==========================================================
    # AUDIT
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
    # REPRESENTATION
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"LearnerProfile("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"display_name={self.display_name!r}"
            f")"
        )

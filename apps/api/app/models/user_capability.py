from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
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


class UserCapability(Base):
    """
    Relationship between a user and a capability.

    This represents the current measured capability
    profile of a user.
    """

    __tablename__ = "user_capabilities"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "capability_id",
            name="uq_user_capability",
        ),
        Index(
            "ix_user_capabilities_user_id",
            "user_id",
        ),
        Index(
            "ix_user_capabilities_capability_id",
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
    # Relationships
    # ==========================================================

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    capability_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("capabilities.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ==========================================================
    # Capability Measurement
    # ==========================================================

    proficiency_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ==========================================================
    # Audit
    # ==========================================================

    last_assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
            f"UserCapability("
            f"user_id={self.user_id!r}, "
            f"capability_id={self.capability_id!r}, "
            f"score={self.score!r}"
            f")"
        )

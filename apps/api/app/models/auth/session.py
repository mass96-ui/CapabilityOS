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


class AuthSession(Base):
    """
    Server-side authentication session.

    Refresh tokens are NEVER stored in plaintext.

    Each refresh token is represented by a SHA-256 hash.
    Rotation creates a new session record while the previous
    token becomes unusable.

    Token families allow refresh-token reuse detection.
    """

    __tablename__ = "auth_sessions"

    __table_args__ = (
        Index(
            "ix_auth_sessions_user_id",
            "user_id",
        ),
        Index(
            "ix_auth_sessions_token_family",
            "token_family",
        ),
        Index(
            "ix_auth_sessions_refresh_token_hash",
            "refresh_token_hash",
            unique=True,
        ),
    )

    # ========================================================
    # Primary Key
    # ========================================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # ========================================================
    # User
    # ========================================================

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ========================================================
    # Refresh Token
    # ========================================================

    refresh_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    token_family: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    # ========================================================
    # Lifecycle
    # ========================================================

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ========================================================
    # Rotation / Reuse Detection
    # ========================================================

    replaced_by_session_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    reuse_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ========================================================
    # Device / Client Information
    # ========================================================

    user_agent: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    device_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ========================================================
    # Audit
    # ========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            f"AuthSession("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"token_family={self.token_family!r}, "
            f"revoked_at={self.revoked_at!r}"
            f")"
        )

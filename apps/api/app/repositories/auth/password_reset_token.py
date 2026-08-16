from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    """Database operations for password reset tokens."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
    ) -> PasswordResetToken:

        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.session.add(token)

        await self.session.flush()

        return token

    async def get_by_token_hash(
        self,
        token_hash: str,
    ) -> PasswordResetToken | None:

        result = await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    async def mark_used(
        self,
        token: PasswordResetToken,
    ) -> None:

        if token.used_at is None:
            token.used_at = datetime.now(timezone.utc)

        await self.session.flush()

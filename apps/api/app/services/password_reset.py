from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.repositories.auth.password_reset_token import (
    PasswordResetTokenRepository,
)
from app.repositories.user import UserRepository
from app.services.auth.refresh import RefreshTokenService
from app.services.email import EmailService
from app.utils.refresh_token import hash_password_reset_token


class PasswordResetService:
    """Secure password reset flow."""

    TOKEN_LENGTH = 32

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.token_repository = PasswordResetTokenRepository(session)

    async def request_reset(
        self,
        email: str,
    ) -> None:
        """
        Initiate a password reset.

        Always returns success to avoid user enumeration.
        """

        user = await self.user_repository.get_by_email(email)

        if user is not None:
            token = secrets.token_urlsafe(self.TOKEN_LENGTH)

            token_hash = hash_password_reset_token(token)

            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES,
            )

            await self.token_repository.create(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            await self.session.commit()

            reset_url = (
                f"{settings.FRONTEND_URL}/reset-password?token={token}"
            )

            message = (
                f"CapabilityOS Password Reset\n\n"
                f"Your password reset link is:\n\n"
                f"{reset_url}\n\n"
                f"This link is valid for {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.\n\n"
                f"If you did not request a password reset, you can safely ignore this email.\n\n"
                f"Regards,\n"
                f"CapabilityOS Team"
            )

            await EmailService._send_raw(
                email=email,
                subject="CapabilityOS Password Reset",
                body=message,
            )

    async def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> User:
        """
        Complete a password reset using a valid token.
        """

        token_hash = hash_password_reset_token(token)

        reset_token = (
            await self.token_repository.get_by_token_hash(
                token_hash=token_hash,
            )
        )

        if reset_token is None:
            raise ValueError("Invalid or expired reset token.")

        now = datetime.now(timezone.utc)

        if reset_token.expires_at <= now:
            raise ValueError("Reset token has expired.")

        user = await self.user_repository.get_by_id(
            reset_token.user_id,
        )

        if user is None:
            raise ValueError("User account no longer exists.")

        from app.utils.password import PasswordManager

        user.password_hash = PasswordManager.hash_password(
            new_password
        )

        await RefreshTokenService.revoke_all_for_user(
            user_id=user.id,
            db=self.session,
        )

        await self.token_repository.mark_used(reset_token)

        await self.session.commit()

        await self.session.refresh(user)

        return user

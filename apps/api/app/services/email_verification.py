from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.auth.email_verification import EmailVerificationOTP
from app.models.user import User
from app.services.email import EmailService
from app.utils.otp import OTPManager
from app.utils.password import PasswordManager


class EmailVerificationService:
    """Handles email verification OTP lifecycle."""

    MAX_ATTEMPTS = 5

    @staticmethod
    async def create_and_send_otp(
        db: AsyncSession,
        user: User,
    ) -> None:
        """
        Invalidate existing OTPs, create a new OTP,
        store only its hash, and send the plaintext OTP by email.
        """

        now = datetime.now(timezone.utc)

        # Invalidate previous unused OTPs.
        await db.execute(
            update(EmailVerificationOTP)
            .where(
                EmailVerificationOTP.user_id == user.id,
                EmailVerificationOTP.used_at.is_(None),
            )
            .values(used_at=now)
        )

        otp = OTPManager.generate_otp()

        otp_hash = PasswordManager.hash_password(otp)

        expires_at = now + timedelta(
            minutes=settings.EMAIL_VERIFICATION_OTP_EXPIRE_MINUTES
        )

        record = EmailVerificationOTP(
            user_id=user.id,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0,
            max_attempts=EmailVerificationService.MAX_ATTEMPTS,
        )

        db.add(record)

        await db.flush()

        # Send plaintext OTP only through email.
        await EmailService.send_verification_otp(
            email=user.email,
            otp=otp,
        )

    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        user: User,
        otp: str,
    ) -> bool:
        """
        Verify the latest active OTP for a user.
        """

        statement = (
            select(EmailVerificationOTP)
            .where(
                EmailVerificationOTP.user_id == user.id,
                EmailVerificationOTP.used_at.is_(None),
            )
            .order_by(
                EmailVerificationOTP.created_at.desc()
            )
        )

        result = await db.execute(statement)

        verification = result.scalars().first()

        if verification is None:
            return False

        now = datetime.now(timezone.utc)

        if verification.attempts >= verification.max_attempts:
            return False

        if verification.expires_at <= now:
            return False

        verification.attempts += 1

        if not PasswordManager.verify_password(
            otp,
            verification.otp_hash,
        ):
            await db.flush()
            return False

        verification.used_at = now

        user.is_verified = True

        await db.flush()

        return True
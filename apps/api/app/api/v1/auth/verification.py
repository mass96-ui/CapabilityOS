from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.user import UserRepository
from app.schemas.email_verification import (
    ResendEmailOTPRequest,
    VerifyEmailOTPRequest,
)
from app.services.email_verification import EmailVerificationService


router = APIRouter(
    prefix="/auth",
    tags=["Email Verification"],
)


@router.post(
    "/verify-email",
    summary="Verify email address using OTP",
)
async def verify_email(
    request: VerifyEmailOTPRequest,
    db: AsyncSession = Depends(get_session),
):
    """Verify a user's email address."""

    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(request.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification request.",
        )

    if user.is_verified:
        return {
            "message": "Email address is already verified."
        }

    success = await EmailVerificationService.verify_otp(
        db=db,
        user=user,
        otp=request.otp,
    )

    if not success:
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP.",
        )

    await db.commit()

    return {
        "message": "Email address verified successfully.",
        "verified": True,
    }


@router.post(
    "/resend-verification",
    summary="Resend email verification OTP",
)
async def resend_verification(
    request: ResendEmailOTPRequest,
    db: AsyncSession = Depends(get_session),
):
    """Generate and send a new verification OTP."""

    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(request.email)

    if user is None:
        # Do not reveal whether an email exists.
        return {
            "message": "If the account exists, a verification OTP has been sent."
        }

    if user.is_verified:
        return {
            "message": "Email address is already verified."
        }

    await EmailVerificationService.create_and_send_otp(
        db=db,
        user=user,
    )

    await db.commit()

    return {
        "message": "If the account exists, a verification OTP has been sent."
    }
from __future__ import annotations

from pydantic import Field

from app.schemas.common import BaseSchema


class VerifyEmailOTPRequest(BaseSchema):
    """Verify an email address using a 6-digit OTP."""

    email: str
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class ResendEmailOTPRequest(BaseSchema):
    """Request a new email verification OTP."""

    email: str
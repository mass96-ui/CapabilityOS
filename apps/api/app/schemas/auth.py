from __future__ import annotations

from pydantic import EmailStr, Field, SecretStr, field_validator

from app.schemas.common import BaseSchema
from app.schemas.user import UserResponse


# ==========================================================
# USER LOGIN
# ==========================================================

class LoginRequest(BaseSchema):
    """User login request."""

    email: EmailStr = Field(
        ...,
        description="Registered email address",
    )

    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password",
    )


# ==========================================================
# USER REGISTRATION
# ==========================================================

class RegisterRequest(BaseSchema):
    """User registration request."""

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    confirm_password: SecretStr

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(
        cls,
        value: SecretStr,
        info,
    ) -> SecretStr:
        password = info.data.get("password")

        if (
            password
            and value.get_secret_value()
            != password.get_secret_value()
        ):
            raise ValueError("Passwords do not match.")

        return value


# ==========================================================
# EMAIL VERIFICATION
# ==========================================================

class VerifyEmailRequest(BaseSchema):
    """Verify email address using a six-digit OTP."""

    email: EmailStr

    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="Six digit email verification OTP",
    )


class ResendVerificationRequest(BaseSchema):
    """Request a new verification OTP."""

    email: EmailStr


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ChangePasswordRequest(BaseSchema):
    """Change password request."""

    current_password: SecretStr

    new_password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    confirm_password: SecretStr

    @field_validator("confirm_password")
    @classmethod
    def validate_new_password_match(
        cls,
        value: SecretStr,
        info,
    ) -> SecretStr:
        new_password = info.data.get("new_password")

        if (
            new_password
            and value.get_secret_value()
            != new_password.get_secret_value()
        ):
            raise ValueError("Passwords do not match.")

        return value


# ==========================================================
# FORGOT PASSWORD
# ==========================================================

class ForgotPasswordRequest(BaseSchema):
    """Forgot password request."""

    email: EmailStr


# ==========================================================
# RESET PASSWORD
# ==========================================================

class ResetPasswordRequest(BaseSchema):
    """Reset password request."""

    token: str

    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    confirm_password: SecretStr

    @field_validator("confirm_password")
    @classmethod
    def validate_passwords(
        cls,
        value: SecretStr,
        info,
    ) -> SecretStr:
        password = info.data.get("password")

        if (
            password
            and value.get_secret_value()
            != password.get_secret_value()
        ):
            raise ValueError("Passwords do not match.")

        return value


# ==========================================================
# REGISTRATION RESPONSE
# IMPORTANT:
# This response intentionally contains NO JWT tokens.
# ==========================================================

class RegistrationResponse(BaseSchema):
    """Response returned after account registration."""

    message: str

    email: EmailStr

    username: str

    is_verified: bool = False


# ==========================================================
# AUTHENTICATION RESPONSE
# Used ONLY after successful authentication.
# ==========================================================

class RefreshTokenRequest(BaseSchema):
    """Request a new access token using a refresh token."""

    refresh_token: str = Field(
        ...,
        min_length=1,
        description="Valid refresh token",
    )


# ==========================================================
# AUTHENTICATION RESPONSE
# ==========================================================

class AuthResponse(BaseSchema):
    """Authentication response containing JWT tokens."""

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

    expires_in: int

    user: UserResponse

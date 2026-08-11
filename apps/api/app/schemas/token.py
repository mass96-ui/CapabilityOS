from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict, Field

from app.schemas.common import BaseSchema


# ==========================================================
# JWT Access Token
# ==========================================================


class Token(BaseSchema):
    """
    Standard JWT authentication response.
    """

    access_token: str = Field(
        ...,
        description="JWT access token",
    )

    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
    )

    token_type: str = Field(
        default="bearer",
        description="Authentication scheme",
    )

    expires_in: int = Field(
        ...,
        description="Access token lifetime in seconds",
    )


# ==========================================================
# Refresh Token Request
# ==========================================================


class RefreshTokenRequest(BaseSchema):
    """
    Request body for refreshing an access token.
    """

    refresh_token: str = Field(
        ...,
        min_length=32,
        description="Refresh token",
    )


# ==========================================================
# Token Payload
# ==========================================================


class TokenPayload(BaseSchema):
    """
    Decoded JWT payload.
    """

    sub: str = Field(
        ...,
        description="User UUID",
    )

    email: str

    username: str

    is_superuser: bool = False

    is_verified: bool = False

    exp: int

    iat: int

    jti: str


# ==========================================================
# Refresh Token Payload
# ==========================================================


class RefreshTokenPayload(BaseSchema):
    """
    Decoded refresh token payload.
    """

    sub: str

    jti: str

    exp: int

    iat: int


# ==========================================================
# Token Metadata
# ==========================================================


class TokenMetadata(BaseSchema):
    """
    Metadata returned when inspecting a token.
    """

    issued_at: datetime

    expires_at: datetime

    token_type: str

    active: bool


# ==========================================================
# Logout Response
# ==========================================================


class LogoutResponse(BaseSchema):
    """
    Response returned after logout.
    """

    success: bool = True

    message: str = "Successfully logged out."


# ==========================================================
# Token Validation Response
# ==========================================================


class TokenValidationResponse(BaseSchema):
    """
    Response returned after validating a token.
    """

    model_config = ConfigDict(from_attributes=True)

    valid: bool

    payload: TokenPayload | None = None
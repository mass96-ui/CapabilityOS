from __future__ import annotations

import bcrypt
import secrets

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import CurrentUserDep, get_db
from app.core.logging import logger
from app.core.rate_limit import rate_limit
from app.models.auth.email_verification import EmailVerificationOTP
from app.repositories.user import UserRepository
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    RefreshTokenRequest,
)
from app.schemas.user import UserResponse
from app.services.auth.refresh import RefreshTokenService
from app.services.password_reset import PasswordResetService
from app.utils.jwt import JWTManager
from app.utils.password import PasswordManager


def _ensure_utc(value: datetime) -> datetime:
    "Normalize database datetimes to timezone-aware UTC."
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# CONFIGURATION
# ============================================================

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


# ============================================================
# OTP GENERATION
# ============================================================


def _generate_otp() -> str:
    """
    Generate a cryptographically secure 6-digit OTP.
    """

    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_otp(otp: str) -> str:
    """
    Hash OTP before storing it in the database.
    """

    return bcrypt.hashpw(
        otp.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def _verify_otp(
    otp: str,
    otp_hash: str,
) -> bool:
    """
    Verify plaintext OTP against stored bcrypt hash.
    """

    try:
        return bcrypt.checkpw(
            otp.encode("utf-8"),
            otp_hash.encode("utf-8"),
        )

    except Exception:
        return False


# ============================================================
# EMAIL SENDING
# ============================================================

from app.services.email import EmailService


async def _send_verification_email(
    email: str,
    first_name: str,
    otp: str,
) -> None:
    """
    Send email without blocking the FastAPI event loop.
    """

    await EmailService.send_verification_otp(
        email=email,
        otp=otp,
        first_name=first_name,
    )


# ============================================================
# CREATE VERIFICATION OTP
# ============================================================


async def _create_verification_otp(
    user_id: str,
    email: str,
    first_name: str,
    db: AsyncSession,
) -> None:
    """
    Invalidate old OTPs, create a new OTP and send it by email.
    """

    # --------------------------------------------------------
    # Invalidate previous unused OTPs
    # --------------------------------------------------------

    await db.execute(
        update(EmailVerificationOTP)
        .where(
            EmailVerificationOTP.user_id == user_id,
            EmailVerificationOTP.used_at.is_(None),
        )
        .values(
            used_at=datetime.now(timezone.utc),
        )
    )

    # --------------------------------------------------------
    # Generate new OTP
    # --------------------------------------------------------

    otp = _generate_otp()

    otp_hash = _hash_otp(otp)

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=OTP_EXPIRY_MINUTES
    )

    otp_record = EmailVerificationOTP(
        user_id=user_id,
        otp_hash=otp_hash,
        expires_at=expires_at,
        attempts=0,
        max_attempts=OTP_MAX_ATTEMPTS,
    )

    db.add(otp_record)

    await db.commit()

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:

        await _send_verification_email(
            email=email,
            first_name=first_name,
            otp=otp,
        )

    except Exception as exc:

        logger.error(
            "Could not send verification email to %s: %s",
            email,
            exc,
        )

        if settings.ENVIRONMENT == "development":

            logger.info(
                "Dev OTP for %s: %s",
                email,
                otp,
            )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Account was created, but the verification email "
                "could not be sent. Please use resend verification."
            ),
        )


# ============================================================
# CREATE AUTH RESPONSE
# ============================================================


async def _create_auth_response(
    user,
    db: AsyncSession,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
    device_name: str | None = None,
) -> AuthResponse:
    """
    Create access and refresh tokens and persist the refresh
    token server-side.

    IMPORTANT:

    This function MUST ONLY be called after the user's
    email has been verified.
    """

    # --------------------------------------------------------
    # CRITICAL SECURITY CHECK
    # --------------------------------------------------------

    if not user.is_verified:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Email address is not verified. "
                "Authentication tokens cannot be issued "
                "until email verification is complete."
            ),
        )

    # --------------------------------------------------------
    # ACCESS TOKEN
    # --------------------------------------------------------

    access_token = JWTManager.create_access_token(
        user_id=user.id,
        email=user.email,
        username=user.username,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
    )

    # --------------------------------------------------------
    # REFRESH TOKEN
    # --------------------------------------------------------

    refresh_token = JWTManager.create_refresh_token(
        user_id=user.id,
    )

    # --------------------------------------------------------
    # SERVER-SIDE REFRESH SESSION
    #
    # IMPORTANT:
    # The raw refresh token is NOT stored.
    #
    # RefreshTokenService hashes it and stores only
    # the deterministic HMAC-SHA256 hash.
    # --------------------------------------------------------

    await RefreshTokenService.create_session(
        user_id=user.id,
        refresh_token=refresh_token,
        db=db,
        user_agent=user_agent,
        ip_address=ip_address,
        device_name=device_name,
    )

    # --------------------------------------------------------
    # COMMIT AUTH SESSION
    # --------------------------------------------------------

    await db.commit()

    # --------------------------------------------------------
    # CREATE RESPONSE
    # --------------------------------------------------------

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


# ============================================================
# INTERNAL AUTHENTICATION HELPER
# ============================================================


async def _authenticate_user(
    login: str,
    password: str,
    db: AsyncSession,
):
    """
    Authenticate a user using email or username.

    IMPORTANT:

    Email verification is REQUIRED before authentication
    tokens can be issued.
    """

    user_repo = UserRepository(db)

    user = await user_repo.get_by_login(login)

    # --------------------------------------------------------
    # User not found
    # --------------------------------------------------------

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Password verification
    # --------------------------------------------------------

    if not PasswordManager.verify_password(
        password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Active account check
    # --------------------------------------------------------

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive.",
        )

    # --------------------------------------------------------
    # CRITICAL SECURITY CHECK
    # --------------------------------------------------------

    if not user.is_verified:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Email address is not verified. "
                "Please verify your email before logging in."
            ),
        )

    return user


# ============================================================
# REGISTER
# ============================================================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=5, window_seconds=60)),
) -> UserResponse:
    """
    Register a new CapabilityOS user.

    SECURITY FLOW:

    1. Create user.
    2. User starts as is_verified=False.
    3. Generate OTP.
    4. Store hashed OTP.
    5. Send OTP by email.
    6. DO NOT issue access token.
    7. DO NOT issue refresh token.
    """

    user_repo = UserRepository(db)

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    if await user_repo.email_exists(request.email):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered.",
        )

    # --------------------------------------------------------
    # Check duplicate username
    # --------------------------------------------------------

    if await user_repo.username_exists(
        request.username
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken.",
        )

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    hashed_pw = PasswordManager.hash_password(
        request.password.get_secret_value()
    )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    user = await user_repo.create(
        email=str(request.email),
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        password_hash=hashed_pw,
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    # --------------------------------------------------------
    # Create and send verification OTP
    # --------------------------------------------------------

    await _create_verification_otp(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        db=db,
    )

    # --------------------------------------------------------
    # CRITICAL:
    #
    # NO TOKENS ARE RETURNED HERE.
    # --------------------------------------------------------

    await db.refresh(user)

    return UserResponse.model_validate(user)


# ============================================================
# VERIFY EMAIL OTP
# ============================================================


@router.post(
    "/verify-email",
    response_model=AuthResponse,
    summary="Verify email and issue authentication tokens",
)
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=5, window_seconds=60)),
) -> AuthResponse:
    """
    Verify a user's email address using OTP.

    ONLY AFTER SUCCESSFUL VERIFICATION:

    - is_verified becomes True
    - access token is created
    - refresh token is created
    - refresh-token session is stored
    """

    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(
        str(request.email)
    )

    # --------------------------------------------------------
    # User not found
    # --------------------------------------------------------

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found for this email address.",
        )

    # --------------------------------------------------------
    # Already verified
    # --------------------------------------------------------

    if user.is_verified:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already verified.",
        )

    # --------------------------------------------------------
    # Get latest unused OTP
    # --------------------------------------------------------

    statement = (
        select(EmailVerificationOTP)
        .where(
            EmailVerificationOTP.user_id == user.id,
            EmailVerificationOTP.used_at.is_(None),
        )
        .order_by(
            EmailVerificationOTP.created_at.desc()
        )
        .limit(1)
    )

    result = await db.execute(statement)

    otp_record = result.scalar_one_or_none()

    if not otp_record:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No active verification OTP found. "
                "Please request a new OTP."
            ),
        )

    # --------------------------------------------------------
    # Check expiration
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    if _ensure_utc(otp_record.expires_at) < now:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Verification OTP has expired. "
                "Please request a new OTP."
            ),
        )

    # --------------------------------------------------------
    # Check attempt limit
    # --------------------------------------------------------

    if (
        otp_record.attempts
        >= otp_record.max_attempts
    ):

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Maximum OTP attempts exceeded. "
                "Please request a new OTP."
            ),
        )

    # --------------------------------------------------------
    # Verify OTP
    # --------------------------------------------------------

    if not _verify_otp(
        request.otp,
        otp_record.otp_hash,
    ):

        otp_record.attempts += 1

        await db.commit()

        remaining = max(
            0,
            otp_record.max_attempts
            - otp_record.attempts,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid verification OTP. "
                f"{remaining} attempt(s) remaining."
            ),
        )

    # --------------------------------------------------------
    # OTP CORRECT
    # --------------------------------------------------------

    otp_record.used_at = datetime.now(timezone.utc)

    user.is_verified = True

    await db.commit()

    await db.refresh(user)

    # --------------------------------------------------------
    # CRITICAL SECURITY POINT
    #
    # Tokens are created ONLY here, after verification.
    #
    # The refresh token is also persisted as a hash inside
    # auth_sessions.
    # --------------------------------------------------------

    return await _create_auth_response(
        user,
        db,
    )


# ============================================================
# RESEND VERIFICATION OTP
# ============================================================


@router.post(
    "/resend-verification",
    response_model=UserResponse,
    summary="Resend email verification OTP",
)
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=3, window_seconds=60)),
) -> UserResponse:
    """
    Generate and send a new email verification OTP.
    """

    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(
        str(request.email)
    )

    # --------------------------------------------------------
    # User not found
    # --------------------------------------------------------

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found for this email address.",
        )

    # --------------------------------------------------------
    # Already verified
    # --------------------------------------------------------

    if user.is_verified:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already verified.",
        )

    # --------------------------------------------------------
    # Generate new OTP
    # --------------------------------------------------------

    await _create_verification_otp(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        db=db,
    )

    await db.refresh(user)

    return UserResponse.model_validate(user)


# ============================================================
# JSON LOGIN
# ============================================================


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate verified user and return access token",
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=10, window_seconds=60)),
) -> AuthResponse:
    """
    Authenticate user using JSON.

    Unverified users cannot receive tokens.
    """

    user = await _authenticate_user(
        login=str(request.email),
        password=request.password.get_secret_value(),
        db=db,
    )

    return await _create_auth_response(
        user,
        db,
    )


# ============================================================
# OAUTH2 TOKEN LOGIN
# ============================================================


@router.post(
    "/token",
    response_model=AuthResponse,
    summary="OAuth2 login for Swagger and OAuth2 clients",
)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=10, window_seconds=60)),
) -> AuthResponse:
    """
    OAuth2-compatible login endpoint.

    Swagger sends:

    username=<email or username>
    password=<password>

    Unverified users cannot receive tokens.
    """

    user = await _authenticate_user(
        login=form_data.username,
        password=form_data.password,
        db=db,
    )

    return await _create_auth_response(
        user,
        db,
    )


# ============================================================
# CURRENT USER
# ============================================================



# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Rotate refresh token and issue new authentication tokens",
)
async def refresh(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=20, window_seconds=60)),
) -> AuthResponse:
    """
    Rotate a valid refresh token.

    Security flow:

    1. Validate the refresh JWT.
    2. Validate the server-side session.
    3. Detect refresh-token reuse.
    4. Revoke the old session.
    5. Create a replacement refresh session.
    6. Issue a new access token.
    7. Return the new refresh token.
    """

    # --------------------------------------------------------
    # ROTATE REFRESH TOKEN
    # --------------------------------------------------------

    try:
        new_refresh_token, new_session = (
            await RefreshTokenService.rotate(
                refresh_token=request.refresh_token,
                db=db,
            )
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to refresh authentication session.",
        )

    # --------------------------------------------------------
    # LOAD USER
    # --------------------------------------------------------

    user_repo = UserRepository(db)

    user = await user_repo.get_by_id(
        new_session.user_id
    )

    if not user:
        await RefreshTokenService.revoke_session(
            refresh_token=new_refresh_token,
            db=db,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
        )

    # --------------------------------------------------------
    # SECURITY CHECKS
    # --------------------------------------------------------

    if not user.is_active:
        await RefreshTokenService.revoke_session(
            refresh_token=new_refresh_token,
            db=db,
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    if not user.is_verified:
        await RefreshTokenService.revoke_session(
            refresh_token=new_refresh_token,
            db=db,
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address is not verified.",
        )

    # --------------------------------------------------------
    # CREATE NEW ACCESS TOKEN
    # --------------------------------------------------------

    access_token = JWTManager.create_access_token(
        user_id=user.id,
        email=user.email,
        username=user.username,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
    )

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    await db.commit()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


# ============================================================
# LOGOUT CURRENT SESSION
# ============================================================

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout the current refresh-token session",
)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=10, window_seconds=60)),
) -> None:
    """
    Revoke exactly one refresh-token session.

    Invalid or already-revoked tokens are treated as logged out.
    """

    await RefreshTokenService.revoke_session(
        refresh_token=request.refresh_token,
        db=db,
    )


# ============================================================
# LOGOUT ALL SESSIONS
# ============================================================

@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout all sessions for the authenticated user",
)
async def logout_all(
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=5, window_seconds=60)),
) -> None:
    """
    Revoke every refresh-token session belonging to
    the currently authenticated user.
    """

    await RefreshTokenService.revoke_all_for_user(
        user_id=current_user.id,
        db=db,
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a password reset email",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=5, window_seconds=60)),
) -> None:
    """
    Initiate a password reset.

    Always returns 202 to avoid user enumeration.
    """

    service = PasswordResetService(db)

    await service.request_reset(
        email=str(request.email),
    )


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password using a reset token",
)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=5, window_seconds=60)),
) -> None:
    """
    Complete a password reset.

    The raw token is consumed and marked as used.
    """

    service = PasswordResetService(db)

    try:
        await service.reset_password(
            token=request.token,
            new_password=request.password.get_secret_value(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user's profile",
)
async def get_me(
    current_user: CurrentUserDep,
) -> UserResponse:
    """
    Return current authenticated user's profile information.
    """

    return UserResponse.model_validate(
        current_user
    )

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings


# ==========================================================
# JWT Configuration
# ==========================================================

ALGORITHM = settings.JWT_ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


# ==========================================================
# JWT Manager
# ==========================================================


class JWTManager:
    """
    CapabilityOS JWT Manager.

    Responsible for:
    - Access Token generation
    - Refresh Token generation
    - Token validation
    - Payload decoding
    """

    @staticmethod
    def create_access_token(
        *,
        user_id: str,
        email: str,
        username: str,
        is_superuser: bool = False,
        is_verified: bool = False,
    ) -> str:
        """
        Generate JWT Access Token.
        """

        now = datetime.now(UTC)

        payload = {
            "sub": user_id,
            "email": email,
            "username": username,
            "is_superuser": is_superuser,
            "is_verified": is_verified,
            "iat": int(now.timestamp()),
            "exp": int(
                (
                    now
                    + timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                ).timestamp()
            ),
            "jti": str(uuid4()),
            "type": "access",
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=ALGORITHM,
        )

    @staticmethod
    def create_refresh_token(
        *,
        user_id: str,
    ) -> str:
        """
        Generate JWT Refresh Token.
        """

        now = datetime.now(UTC)

        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int(
                (
                    now
                    + timedelta(
                        days=REFRESH_TOKEN_EXPIRE_DAYS
                    )
                ).timestamp()
            ),
            "jti": str(uuid4()),
            "type": "refresh",
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=ALGORITHM,
        )

    @staticmethod
    def decode_token(
        token: str,
    ) -> dict:
        """
        Decode any JWT token.
        """

        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    @staticmethod
    def verify_access_token(
        token: str,
    ) -> dict:
        """
        Verify Access Token.
        """

        payload = JWTManager.decode_token(token)

        if payload.get("type") != "access":
            raise JWTError("Invalid access token.")

        return payload

    @staticmethod
    def verify_refresh_token(
        token: str,
    ) -> dict:
        """
        Verify Refresh Token.
        """

        payload = JWTManager.decode_token(token)

        if payload.get("type") != "refresh":
            raise JWTError("Invalid refresh token.")

        return payload

    @staticmethod
    def get_subject(
        token: str,
    ) -> str:
        """
        Return authenticated user UUID.
        """

        payload = JWTManager.verify_access_token(token)

        return payload["sub"]

    @staticmethod
    def is_token_expired(
        token: str,
    ) -> bool:
        """
        Check whether token has expired.
        """

        try:
            JWTManager.decode_token(token)
            return False

        except JWTError:
            return True
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.auth.session import AuthSession
from app.repositories.auth.session import AuthSessionRepository
from app.utils.jwt import JWTManager
from app.utils.refresh_token import hash_refresh_token


def _ensure_utc(dt: datetime) -> datetime:
    """
    Normalize a datetime to timezone-aware UTC.

    SQLite may return DateTime(timezone=True) values
    as naive datetimes.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)

    return dt.astimezone(UTC)


class RefreshTokenService:
    """
    Secure server-side refresh-token lifecycle management.
    """

    @staticmethod
    async def create_session(
        *,
        user_id: str,
        refresh_token: str,
        db: AsyncSession,
        token_family: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
        device_name: str | None = None,
    ) -> AuthSession:

        repository = AuthSessionRepository(db)

        now = datetime.now(UTC)

        expires_at = now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        session = await repository.create(
            user_id=user_id,
            refresh_token_hash=hash_refresh_token(
                refresh_token
            ),
            token_family=(
                token_family
                or str(uuid4())
            ),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
        )

        return session

    @staticmethod
    async def validate(
        *,
        refresh_token: str,
        db: AsyncSession,
    ) -> tuple[dict, AuthSession]:

        try:
            payload = JWTManager.verify_refresh_token(
                refresh_token
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        token_hash = hash_refresh_token(
            refresh_token
        )

        repository = AuthSessionRepository(db)

        session = (
            await repository.get_by_refresh_token_hash(
                token_hash
            )
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        if session.revoked_at is not None:

            await repository.revoke_family(
                session.token_family,
                mark_reuse_detected=True,
            )

            await db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Refresh token reuse detected. "
                    "Please authenticate again."
                ),
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        # ------------------------------------------------
        # DATABASE EXPIRATION
        # ------------------------------------------------

        now = datetime.now(UTC)

        # SQLite may return this as a naive datetime.
        expires_at = _ensure_utc(
            session.expires_at
        )

        if expires_at <= now:

            await repository.revoke(session)

            await db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        if user_id != session.user_id:

            await repository.revoke_family(
                session.token_family,
                mark_reuse_detected=True,
            )

            await db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        await repository.touch(session)

        await db.commit()

        return payload, session

    @staticmethod
    async def rotate(
        *,
        refresh_token: str,
        db: AsyncSession,
        user_agent: str | None = None,
        ip_address: str | None = None,
        device_name: str | None = None,
    ) -> tuple[str, AuthSession]:

        _, old_session = (
            await RefreshTokenService.validate(
                refresh_token=refresh_token,
                db=db,
            )
        )

        repository = AuthSessionRepository(db)

        new_refresh_token = (
            JWTManager.create_refresh_token(
                user_id=old_session.user_id,
            )
        )

        new_session = (
            await RefreshTokenService.create_session(
                user_id=old_session.user_id,
                refresh_token=new_refresh_token,
                db=db,
                token_family=old_session.token_family,
                user_agent=(
                    user_agent
                    or old_session.user_agent
                ),
                ip_address=(
                    ip_address
                    or old_session.ip_address
                ),
                device_name=(
                    device_name
                    or old_session.device_name
                ),
            )
        )

        await repository.revoke(old_session)

        old_session.replaced_by_session_id = (
            new_session.id
        )

        await repository.touch(old_session)

        await db.commit()

        return (
            new_refresh_token,
            new_session,
        )

    @staticmethod
    async def revoke_session(
        *,
        refresh_token: str,
        db: AsyncSession,
    ) -> None:

        token_hash = hash_refresh_token(
            refresh_token
        )

        repository = AuthSessionRepository(db)

        session = (
            await repository.get_by_refresh_token_hash(
                token_hash
            )
        )

        if session is not None:
            await repository.revoke(session)
            await db.commit()

    @staticmethod
    async def revoke_all_for_user(
        *,
        user_id: str,
        db: AsyncSession,
    ) -> None:

        repository = AuthSessionRepository(db)

        await repository.revoke_all_for_user(
            user_id
        )

        await db.commit()

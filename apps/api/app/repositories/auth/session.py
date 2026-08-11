from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.session import AuthSession


class AuthSessionRepository:
    """Database operations for authentication sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: str,
        refresh_token_hash: str,
        token_family: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
        device_name: str | None = None,
    ) -> AuthSession:

        auth_session = AuthSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            token_family=token_family,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
        )

        self.session.add(auth_session)
        await self.session.flush()

        return auth_session

    async def get_by_refresh_token_hash(
        self,
        refresh_token_hash: str,
    ) -> AuthSession | None:

        statement = select(AuthSession).where(
            AuthSession.refresh_token_hash == refresh_token_hash
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        session_id: str,
    ) -> AuthSession | None:

        statement = select(AuthSession).where(
            AuthSession.id == session_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def revoke(
        self,
        auth_session: AuthSession,
    ) -> None:

        if auth_session.revoked_at is None:
            auth_session.revoked_at = datetime.now(UTC)

        await self.session.flush()

    async def revoke_family(
        self,
        token_family: str,
        *,
        mark_reuse_detected: bool = False,
    ) -> None:

        values = {
            "revoked_at": datetime.now(UTC),
        }

        if mark_reuse_detected:
            values["reuse_detected"] = True

        await self.session.execute(
            update(AuthSession)
            .where(
                AuthSession.token_family == token_family,
                AuthSession.revoked_at.is_(None),
            )
            .values(**values)
        )

        await self.session.flush()

    async def revoke_all_for_user(
        self,
        user_id: str,
    ) -> None:

        await self.session.execute(
            update(AuthSession)
            .where(
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(UTC)
            )
        )

        await self.session.flush()

    async def touch(
        self,
        auth_session: AuthSession,
    ) -> None:

        auth_session.last_used_at = datetime.now(UTC)

        await self.session.flush()

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ============================================================
# Database Engine
# ============================================================

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# ============================================================
# Session Factory
# ============================================================

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# ============================================================
# Dependency
# ============================================================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a database session for each request.

    The session is automatically closed after the request
    completes.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
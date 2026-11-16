from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_session

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    summary="Health Check",
)
async def health_check() -> dict:
    """
    Basic health endpoint used by:

    - Docker health checks
    - Kubernetes probes
    - Load balancers
    - Monitoring systems
    """

    return {
        "success": True,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/ready",
    summary="Readiness Check",
)
async def readiness_check(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """
    Readiness probe that verifies the database is accepting queries.
    """

    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from None

    return {
        "success": True,
        "status": "ready",
    }


@router.get(
    "/live",
    summary="Liveness Check",
)
async def liveness_check() -> dict:
    """
    Liveness probe.

    Used by orchestrators such as Kubernetes.
    """

    return {
        "success": True,
        "status": "alive",
    }
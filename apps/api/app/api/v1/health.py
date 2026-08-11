from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/ready",
    summary="Readiness Check",
)
async def readiness_check() -> dict:
    """
    Readiness probe.

    Future versions will verify:
    - Database connectivity
    - Redis
    - External services
    """

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
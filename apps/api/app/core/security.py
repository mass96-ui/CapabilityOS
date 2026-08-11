from __future__ import annotations

from typing import List

from app.core.config import settings


def get_cors_origins() -> List[str]:
    """
    Return allowed CORS origins.
    """
    return settings.cors_origins


def get_trusted_hosts() -> List[str]:
    """
    Return trusted hosts for TrustedHostMiddleware.
    """
    return settings.trusted_hosts
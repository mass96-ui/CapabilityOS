from __future__ import annotations

import logging
import time
from collections import defaultdict
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status

from app.core.config import settings

logger = logging.getLogger("capabilityos")


class RateLimiter:
    """
    In-memory sliding-window rate limiter.

    This implementation is intentionally simple and process-local.

    Limitations:

    - State is not shared across multiple API workers.
    - Not suitable for distributed deployments.
    - For production horizontal scaling, replace with
      a Redis-backed implementation.

    For the current single-process deployment model, this
    provides basic protection against brute-force attacks
    on sensitive authentication endpoints.
    """

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """
        Return True if the request is within the rate limit.

        Parameters
        ----------
        key : str
            Identifier for the rate limit bucket (e.g. IP + endpoint).
        limit : int
            Maximum number of requests allowed in the window.
        window_seconds : int
            Sliding window duration in seconds.
        """

        now = time.time()

        timestamps = self._requests[key]

        cutoff = now - window_seconds

        self._requests[key] = [
            ts for ts in timestamps if ts > cutoff
        ]

        if len(self._requests[key]) >= limit:
            return False

        self._requests[key].append(now)

        return True

    def cleanup(self) -> None:
        """
        Remove stale entries to prevent unbounded memory growth.
        """

        now = time.time()

        for key in list(self._requests.keys()):
            self._requests[key] = [
                ts for ts in self._requests[key]
                if ts > now - 3600
            ]

            if not self._requests[key]:
                del self._requests[key]


_rate_limiter = RateLimiter()


def _client_key(request: Request) -> str:
    """
    Build a rate-limit key from the client IP and endpoint path.
    """

    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    return f"{client_ip}:{request.url.path}"


def rate_limit(
    limit: int | None = None,
    window_seconds: int | None = None,
) -> Callable:
    """
    FastAPI dependency factory for rate limiting.

    Parameters
    ----------
    limit : int, optional
        Maximum requests in the window. Defaults to
        ``settings.RATE_LIMIT_REQUESTS``.
    window_seconds : int, optional
        Window duration in seconds. Defaults to
        ``settings.RATE_LIMIT_WINDOW_SECONDS``.
    """

    limit = limit or settings.RATE_LIMIT_REQUESTS
    window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS

    async def dependency(request: Request) -> None:
        key = _client_key(request)

        if not _rate_limiter.is_allowed(
            key=key,
            limit=limit,
            window_seconds=window_seconds,
        ):
            logger.warning(
                "Rate limit exceeded | key=%s | path=%s",
                key,
                request.url.path,
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

    return dependency

from __future__ import annotations

import logging
import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("capabilityos")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attach a unique request ID to every request.

    Behavior:

    - If the client sends ``X-Request-ID``, reuse it.
    - Otherwise generate a cryptographically secure random ID.
    - Attach it to ``request.state.request_id``.
    - Return it in the ``X-Request-ID`` response header.
    - Make it available to structured logging.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        request_id = request.headers.get("x-request-id")

        if not request_id:
            request_id = secrets.token_urlsafe(16)

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response

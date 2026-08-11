from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("capabilityos")


class ServiceError(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        error_code: str = "SERVICE_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class NotFoundError(ServiceError):
    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(ServiceError):
    def __init__(
        self,
        message: str = "Conflict",
        error_code: str = "CONFLICT",
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT,
        )


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _json_safe(value: Any) -> Any:
    """
    Convert values that cannot be serialized by JSONResponse
    into JSON-safe values.

    FastAPI validation errors can contain raw bytes when the
    request body is malformed or uses an unexpected content type.
    """

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]

    return value


def _response(
    request: Request,
    *,
    status_code: int,
    message: str,
    code: str,
    details: Any | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "success": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": _request_id(request),
        "error": {
            "code": code,
            "message": message,
        },
    }

    if details is not None:
        payload["error"]["details"] = _json_safe(details)

    return JSONResponse(
        status_code=status_code,
        content=payload,
    )


async def handle_service_error(
    request: Request,
    exc: ServiceError,
) -> JSONResponse:
    logger.error(
        "ServiceError [%s]: %s | request_id=%s",
        exc.error_code,
        exc.message,
        _request_id(request),
    )

    return _response(
        request,
        status_code=exc.status_code,
        message=exc.message,
        code=exc.error_code,
    )


async def handle_http_exception(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    logger.warning(
        "HTTPException: %s | request_id=%s",
        exc.detail,
        _request_id(request),
    )

    return _response(
        request,
        status_code=exc.status_code,
        message=str(exc.detail),
        code="HTTP_ERROR",
    )


async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "ValidationError | request_id=%s",
        _request_id(request),
    )

    details = _json_safe(exc.errors())

    return _response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation failed",
        code="VALIDATION_ERROR",
        details=details,
    )


async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled exception | request_id=%s",
        _request_id(request),
    )

    return _response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal Server Error",
        code="INTERNAL_SERVER_ERROR",
    )
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    """
    Production JSON log formatter.

    Every log emitted by CapabilityOS follows a structured JSON format
    suitable for ELK, Loki, Datadog, CloudWatch, Splunk, or OpenTelemetry.
    """

    RESERVED_FIELDS = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "application": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key in self.RESERVED_FIELDS:
                continue

            if key == "request_id":
                continue

            payload[key] = value

        return json.dumps(payload, default=str)


def configure_logging() -> logging.Logger:
    """
    Configure the global CapabilityOS logger.

    Safe to call multiple times.
    """

    logger = logging.getLogger("capabilityos")

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.setLevel(settings.LOG_LEVEL.upper())

    logger.propagate = False
    logger.addHandler(handler)

    return logger


logger = configure_logging()
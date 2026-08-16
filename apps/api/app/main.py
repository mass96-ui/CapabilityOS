from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api import api_router
from app.api.v1.auth import router as auth_router
from app.core.config import get_settings
from app.core.exceptions import (
    ServiceError,
    handle_http_exception,
    handle_service_error,
    handle_unexpected_exception,
    handle_validation_error,
)
from app.core.logging import logger
from app.core.middleware import RequestIDMiddleware
from app.core.security import (
    get_cors_origins,
    get_trusted_hosts,
)
from app.database.init_db import initialize_database


settings = get_settings()


# ==========================================================
# APPLICATION LIFECYCLE
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle.
    """

    logger.info("Starting CapabilityOS API...")

    await initialize_database()

    logger.info("CapabilityOS API started successfully.")

    yield

    logger.info("CapabilityOS API shutting down...")


# ==========================================================
# APPLICATION FACTORY
# ==========================================================

def create_application() -> FastAPI:

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    )

    # ======================================================
    # CORS
    # ======================================================

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Request-ID"],
    )

    app.add_middleware(RequestIDMiddleware)

    # ======================================================
    # TRUSTED HOSTS
    # ======================================================

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=get_trusted_hosts(),
    )

    # ======================================================
    # EXCEPTION HANDLERS
    # ======================================================

    app.add_exception_handler(
        ServiceError,
        handle_service_error,
    )

    app.add_exception_handler(
        HTTPException,
        handle_http_exception,
    )

    app.add_exception_handler(
        RequestValidationError,
        handle_validation_error,
    )

    app.add_exception_handler(
        Exception,
        handle_unexpected_exception,
    )

    # ======================================================
    # API ROUTER
    # ======================================================

    app.include_router(
        api_router,
        prefix="/api",
    )

    # ======================================================
    # AUTHENTICATION
    # ======================================================

    app.include_router(
        auth_router,
        prefix="/api/v1",
    )

    # ======================================================
    # ROOT
    # ======================================================

    @app.get(
        "/",
        tags=["Root"],
    )
    async def root() -> dict[str, str]:

        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "status": "running",
        }

    return app


app = create_application()

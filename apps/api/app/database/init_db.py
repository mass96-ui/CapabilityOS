from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

import app.models  # noqa: F401
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

logger = logging.getLogger("capabilityos.database")

_ALEMBIC_DIR = Path(__file__).parent.parent.parent


def _run_alembic(command: str) -> None:
    """
    Run an Alembic CLI command in the alembic directory.
    """
    result = subprocess.run(
        [sys.executable, "-m", "alembic"] + command.split(),
        cwd=_ALEMBIC_DIR,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Alembic {' '.join(command)} failed: {result.stderr}"
        )


async def create_database() -> None:
    """
    Create all database tables using Alembic migrations.

    This function is executed during application startup.
    """
    _run_alembic("upgrade head")
    logger.info("Database tables created successfully.")


async def drop_database() -> None:
    """
    Drop all database tables using Alembic migrations.

    WARNING:
    Only use this in development or automated tests.
    """
    _run_alembic("downgrade base")
    logger.warning("Database tables dropped.")


async def check_database_connection() -> bool:
    """
    Verify that the database connection is working.
    """

    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))

        logger.info("Database connection successful.")
        return True

    except Exception as exc:
        logger.exception("Database connection failed: %s", exc)
        return False


async def initialize_database() -> None:
    """
    Initialize the database.

    Startup sequence:

    1. Verify database connection.
    2. Create all tables.
    """

    connected = await check_database_connection()

    if not connected:
        raise RuntimeError("Unable to connect to the database.")

    if settings.ENVIRONMENT == "production":
        logger.info("Production environment detected; skipping automatic schema creation.")
    else:
        await create_database()

    logger.info("Database initialization completed successfully.")

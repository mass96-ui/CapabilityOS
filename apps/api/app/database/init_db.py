from __future__ import annotations

import logging

from sqlalchemy import text

import app.models  # noqa: F401
from app.database.base import Base
from app.database.session import engine

logger = logging.getLogger("capabilityos.database")


async def create_database() -> None:
    """
    Create all database tables.

    This function is executed during application startup.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully.")


async def drop_database() -> None:
    """
    Drop all database tables.

    WARNING:
    Only use this in development or automated tests.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

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

    await create_database()

    logger.info("Database initialization completed successfully.")
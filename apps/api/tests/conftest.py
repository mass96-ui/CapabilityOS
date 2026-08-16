from __future__ import annotations

import asyncio
import pytest
from fastapi.testclient import TestClient

from app.core.rate_limit import _rate_limiter
from app.database.init_db import drop_database, initialize_database
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    async def setup_and_teardown():
        await drop_database()
        await initialize_database()
    asyncio.run(setup_and_teardown())


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    _rate_limiter._requests.clear()
    yield
    _rate_limiter._requests.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

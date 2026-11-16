from app.database.session import get_session
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CapabilityOS" in data["message"]
    assert data["status"] == "running"


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"


def test_readiness_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "ready"


def test_readiness_endpoint_reports_database_unavailable(
    client: TestClient,
    monkeypatch,
) -> None:
    class UnavailableSession:
        async def execute(self, statement):
            raise SQLAlchemyError("sensitive database details")

    async def get_unavailable_session():
        yield UnavailableSession()

    monkeypatch.setitem(
        app.dependency_overrides,
        get_session,
        get_unavailable_session,
    )

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["error"]["message"] == "Database unavailable"
    assert "sensitive database details" not in response.text


def test_liveness_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "alive"

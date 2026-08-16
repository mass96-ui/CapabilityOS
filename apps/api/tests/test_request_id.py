from __future__ import annotations

from fastapi.testclient import TestClient


def test_request_id_header_present(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_request_id_reuses_incoming_header(client: TestClient) -> None:
    request_id = "test-request-id-123"

    response = client.get(
        "/",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_request_id_generates_unique_values(client: TestClient) -> None:
    ids = set()

    for _ in range(10):
        response = client.get("/")
        ids.add(response.headers["X-Request-ID"])

    assert len(ids) == 10

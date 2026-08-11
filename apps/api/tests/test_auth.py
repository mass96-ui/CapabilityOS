from __future__ import annotations

from fastapi.testclient import TestClient

import app.api.v1.auth as auth_module


def _message(response) -> str:
    data = response.json()
    return (
        data.get("error", {}).get("message")
        or data.get("detail", "")
    )


def test_auth_production_flow(
    client: TestClient,
    monkeypatch,
) -> None:
    """
    Production authentication lifecycle.

    Covers:
    - registration
    - duplicate email/username protection
    - OTP verification
    - unverified login rejection
    - verified login
    - invalid password
    - authenticated /me
    - invalid access token
    - refresh-token rotation
    - old refresh-token rejection
    - single-session logout
    - logout-all
    - unauthorized logout-all
    """

    captured: dict[str, str] = {}

    async def fake_send_verification_email(
        email: str,
        first_name: str,
        otp: str,
    ) -> None:
        captured["email"] = email
        captured["first_name"] = first_name
        captured["otp"] = otp

    monkeypatch.setattr(
        auth_module,
        "_send_verification_email",
        fake_send_verification_email,
    )

    # ========================================================
    # 1. REGISTER
    # ========================================================

    register_payload = {
        "first_name": "Test",
        "last_name": "Learner",
        "username": "testlearner",
        "email": "learner@capabilityos.dev",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert "access_token" not in data
    assert "refresh_token" not in data
    assert data["is_verified"] is False

    assert captured["email"] == register_payload["email"]
    assert captured["first_name"] == "Test"
    assert len(captured["otp"]) == 6
    assert captured["otp"].isdigit()

    verification_otp = captured["otp"]

    # ========================================================
    # 2. DUPLICATE EMAIL
    # ========================================================

    duplicate_email = {
        **register_payload,
        "username": "differentusername",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=duplicate_email,
    )

    assert response.status_code == 400
    assert "already registered" in _message(response).lower()

    # ========================================================
    # 3. DUPLICATE USERNAME
    # ========================================================

    duplicate_username = {
        **register_payload,
        "email": "otheremail@capabilityos.dev",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=duplicate_username,
    )

    assert response.status_code == 400
    assert "already taken" in _message(response).lower()

    # ========================================================
    # 4. LOGIN BEFORE VERIFICATION
    # ========================================================

    login_payload = {
        "email": register_payload["email"],
        "password": register_payload["password"],
    }

    response = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    assert response.status_code == 403
    assert "not verified" in _message(response).lower()

    # ========================================================
    # 5. WRONG OTP
    # ========================================================

    wrong_otp = (
        "000000"
        if verification_otp != "000000"
        else "111111"
    )

    response = client.post(
        "/api/v1/auth/verify-email",
        json={
            "email": register_payload["email"],
            "otp": wrong_otp,
        },
    )

    assert response.status_code == 400

    # ========================================================
    # 6. CORRECT OTP
    # ========================================================

    response = client.post(
        "/api/v1/auth/verify-email",
        json={
            "email": register_payload["email"],
            "otp": verification_otp,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["user"]["is_verified"] is True
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"

    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    # ========================================================
    # 7. OTP REUSE MUST FAIL
    # ========================================================

    response = client.post(
        "/api/v1/auth/verify-email",
        json={
            "email": register_payload["email"],
            "otp": verification_otp,
        },
    )

    assert response.status_code == 400
    assert "already verified" in _message(response).lower()

    # ========================================================
    # 8. VERIFIED LOGIN
    # ========================================================

    response = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    assert response.status_code == 200, response.text

    login_data = response.json()

    assert login_data["access_token"]
    assert login_data["refresh_token"]

    # ========================================================
    # 9. INVALID PASSWORD
    # ========================================================

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": register_payload["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert "invalid email/username or password" in (
        _message(response).lower()
    )

    # ========================================================
    # 10. AUTHENTICATED /ME
    # ========================================================

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert response.status_code == 200

    me = response.json()

    assert me["email"] == register_payload["email"]
    assert me["username"] == register_payload["username"]
    assert me["is_verified"] is True

    # ========================================================
    # 11. /ME WITHOUT TOKEN
    # ========================================================

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401

    # ========================================================
    # 12. /ME INVALID TOKEN
    # ========================================================

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid_token_123"
        },
    )

    assert response.status_code == 401

    # ========================================================
    # 13. REFRESH TOKEN ROTATION
    # ========================================================

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 200, response.text

    refresh_data = response.json()

    rotated_access_token = refresh_data["access_token"]
    rotated_refresh_token = refresh_data["refresh_token"]

    assert rotated_access_token
    assert rotated_refresh_token
    assert rotated_refresh_token != refresh_token

    # ========================================================
    # 14. OLD REFRESH TOKEN MUST FAIL
    # ========================================================

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 401

    # ========================================================
    # 15. SINGLE SESSION LOGOUT
    # ========================================================

    response = client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": rotated_refresh_token
        },
    )

    assert response.status_code == 204

    # Revoked session must not refresh.
    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": rotated_refresh_token
        },
    )

    assert response.status_code == 401

    # ========================================================
    # 16. CREATE SECOND SESSION
    # ========================================================

    response = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    assert response.status_code == 200

    second_login = response.json()

    second_access_token = second_login["access_token"]
    second_refresh_token = second_login["refresh_token"]

    assert second_access_token
    assert second_refresh_token

    # ========================================================
    # 17. LOGOUT-ALL
    # ========================================================

    response = client.post(
        "/api/v1/auth/logout-all",
        headers={
            "Authorization": f"Bearer {second_access_token}"
        },
    )

    assert response.status_code == 204

    # ========================================================
    # 18. ALL REFRESH SESSIONS MUST BE REVOKED
    # ========================================================

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": second_refresh_token
        },
    )

    assert response.status_code == 401

    # ========================================================
    # 19. ACCESS TOKEN REMAINS VALID UNTIL EXPIRATION
    # ========================================================

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {second_access_token}"
        },
    )

    assert response.status_code == 200

    # ========================================================
    # 20. LOGOUT-ALL REQUIRES AUTHENTICATION
    # ========================================================

    response = client.post("/api/v1/auth/logout-all")

    assert response.status_code == 401

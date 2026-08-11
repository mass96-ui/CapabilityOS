from __future__ import annotations

from fastapi.testclient import TestClient

import app.api.v1.auth as auth_module


def test_auth_flow(
    client: TestClient,
    monkeypatch,
) -> None:
    """
    Complete authentication flow.

    Security flow:

    1. Register unverified user.
    2. No tokens are issued during registration.
    3. Login is rejected until email verification.
    4. Verify OTP.
    5. Authentication tokens are issued.
    6. Access protected /me endpoint.
    7. Test invalid authentication cases.
    """

    # ========================================================
    # Capture verification OTP instead of sending real email
    # ========================================================

    captured = {}

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

    reg_response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    assert reg_response.status_code == 201, reg_response.text

    reg_data = reg_response.json()

    # Registration MUST NOT return authentication tokens.
    assert "access_token" not in reg_data
    assert "refresh_token" not in reg_data

    assert reg_data["email"] == "learner@capabilityos.dev"
    assert reg_data["username"] == "testlearner"

    # User must start unverified.
    assert reg_data["is_verified"] is False

    # OTP should have been generated and captured.
    assert captured["email"] == "learner@capabilityos.dev"
    assert captured["first_name"] == "Test"
    assert captured["otp"]
    assert len(captured["otp"]) == 6
    assert captured["otp"].isdigit()

    verification_otp = captured["otp"]

    # ========================================================
    # 2. DUPLICATE EMAIL
    # ========================================================

    dup_email_payload = {
        "first_name": "Duplicate",
        "last_name": "User",
        "username": "uniqueusername",
        "email": "learner@capabilityos.dev",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }

    dup_res = client.post(
        "/api/v1/auth/register",
        json=dup_email_payload,
    )

    assert dup_res.status_code == 400

    dup_msg = (
        dup_res.json()
        .get("error", {})
        .get("message")
        or dup_res.json().get("detail", "")
    )

    assert "already registered" in dup_msg.lower()

    # ========================================================
    # 3. DUPLICATE USERNAME
    # ========================================================

    dup_uname_payload = {
        "first_name": "Duplicate",
        "last_name": "User",
        "username": "testlearner",
        "email": "otheremail@capabilityos.dev",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }

    dup_u_res = client.post(
        "/api/v1/auth/register",
        json=dup_uname_payload,
    )

    assert dup_u_res.status_code == 400

    dup_u_msg = (
        dup_u_res.json()
        .get("error", {})
        .get("message")
        or dup_u_res.json().get("detail", "")
    )

    assert "already taken" in dup_u_msg.lower()

    # ========================================================
    # 4. LOGIN BEFORE EMAIL VERIFICATION
    # ========================================================

    login_payload = {
        "email": "learner@capabilityos.dev",
        "password": "Password123!",
    }

    unverified_login_res = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    # Security requirement:
    # unverified users MUST NOT receive tokens.
    assert unverified_login_res.status_code == 403

    unverified_msg = (
        unverified_login_res.json()
        .get("error", {})
        .get("message")
        or unverified_login_res.json().get("detail", "")
    )

    assert "not verified" in unverified_msg.lower()

    # ========================================================
    # 5. VERIFY EMAIL OTP
    # ========================================================

    verify_payload = {
        "email": "learner@capabilityos.dev",
        "otp": verification_otp,
    }

    verify_res = client.post(
        "/api/v1/auth/verify-email",
        json=verify_payload,
    )

    assert verify_res.status_code == 200, verify_res.text

    verify_data = verify_res.json()

    assert "access_token" in verify_data
    assert "refresh_token" in verify_data
    assert verify_data["token_type"] == "bearer"

    assert (
        verify_data["user"]["email"]
        == "learner@capabilityos.dev"
    )

    assert verify_data["user"]["is_verified"] is True

    access_token = verify_data["access_token"]
    refresh_token = verify_data["refresh_token"]

    assert access_token
    assert refresh_token

    # ========================================================
    # 6. LOGIN AFTER VERIFICATION
    # ========================================================

    login_res = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    assert login_res.status_code == 200, login_res.text

    login_data = login_res.json()

    assert "access_token" in login_data
    assert "refresh_token" in login_data

    assert (
        login_data["user"]["email"]
        == "learner@capabilityos.dev"
    )

    # ========================================================
    # 7. LOGIN WITH INVALID PASSWORD
    # ========================================================

    bad_login_payload = {
        "email": "learner@capabilityos.dev",
        "password": "WrongPassword123!",
    }

    bad_login_res = client.post(
        "/api/v1/auth/login",
        json=bad_login_payload,
    )

    assert bad_login_res.status_code == 401

    bad_login_msg = (
        bad_login_res.json()
        .get("error", {})
        .get("message")
        or bad_login_res.json().get("detail", "")
    )

    assert "invalid email/username or password" in (
        bad_login_msg.lower()
    )

    # ========================================================
    # 8. GET /auth/me WITH VALID ACCESS TOKEN
    # ========================================================

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    me_res = client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert me_res.status_code == 200, me_res.text

    me_data = me_res.json()

    assert me_data["email"] == "learner@capabilityos.dev"
    assert me_data["username"] == "testlearner"
    assert me_data["first_name"] == "Test"
    assert me_data["last_name"] == "Learner"
    assert me_data["is_verified"] is True

    # ========================================================
    # 9. GET /auth/me WITHOUT TOKEN
    # ========================================================

    no_token_res = client.get(
        "/api/v1/auth/me"
    )

    assert no_token_res.status_code == 401

    # ========================================================
    # 10. GET /auth/me WITH INVALID TOKEN
    # ========================================================

    bad_token_res = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid_token_123"
        },
    )

    assert bad_token_res.status_code == 401

    # ========================================================
    # 11. REFRESH TOKEN
    # ========================================================

    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert refresh_res.status_code == 200, refresh_res.text

    refresh_data = refresh_res.json()

    assert "access_token" in refresh_data
    assert "refresh_token" in refresh_data

    assert refresh_data["access_token"]
    assert refresh_data["refresh_token"]

    # Refresh-token rotation should produce a new token.
    assert (
        refresh_data["refresh_token"]
        != refresh_token
    )

    # ========================================================
    # 12. OLD REFRESH TOKEN MUST NO LONGER WORK
    # ========================================================

    old_refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
    )

    assert old_refresh_res.status_code == 401

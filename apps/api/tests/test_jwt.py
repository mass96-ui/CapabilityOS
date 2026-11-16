from __future__ import annotations

import base64
import json
from datetime import UTC, datetime, timedelta

import app.utils.jwt as jwt_module
import pytest
from app.core.config import Settings
from app.utils.jwt import JWTManager
from jose import JWTError
from jose import jwt as jose_jwt
from pydantic import ValidationError


def test_jwt_algorithm_defaults_to_hs256(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)

    assert Settings(_env_file=None).JWT_ALGORITHM == "HS256"


@pytest.mark.parametrize(
    "algorithm",
    ["RS256", "none", "", " ", "hs256", "HS256 "],
)
def test_settings_rejects_unsupported_jwt_algorithms(
    algorithm: str,
) -> None:
    with pytest.raises(
        ValidationError,
        match="JWT_ALGORITHM must be one of: HS256",
    ):
        Settings(_env_file=None, JWT_ALGORITHM=algorithm)


def test_settings_rejects_unsupported_jwt_algorithm_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_ALGORITHM", "HS384")

    with pytest.raises(
        ValidationError,
        match="JWT_ALGORITHM must be one of: HS256",
    ):
        Settings(_env_file=None)


@pytest.fixture
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    secret = "jwt-regression-test-secret"
    monkeypatch.setattr(jwt_module.settings, "JWT_SECRET_KEY", secret)
    return secret


def _encoded_header(algorithm: str) -> str:
    header = json.dumps(
        {"alg": algorithm, "typ": "JWT"},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(header).rstrip(b"=").decode()


def test_decode_rejects_token_with_altered_algorithm_header(
    jwt_secret: str,
) -> None:
    token = JWTManager.create_access_token(
        user_id="user-id",
        email="user@example.com",
        username="user",
    )
    _, payload, signature = token.split(".")
    altered_token = f"{_encoded_header('HS384')}.{payload}.{signature}"

    with pytest.raises(JWTError):
        JWTManager.decode_token(altered_token)


def test_decode_rejects_token_signed_with_unexpected_algorithm(
    jwt_secret: str,
) -> None:
    payload = {
        "sub": "user-id",
        "exp": int((datetime.now(UTC) + timedelta(minutes=1)).timestamp()),
    }
    token = jose_jwt.encode(
        payload,
        jwt_secret,
        algorithm="HS384",
    )

    with pytest.raises(JWTError):
        JWTManager.decode_token(token)


def test_decode_rejects_tampered_signature(jwt_secret: str) -> None:
    token = JWTManager.create_access_token(
        user_id="user-id",
        email="user@example.com",
        username="user",
    )
    header, payload, signature = token.split(".")
    replacement = "A" if signature[0] != "A" else "B"
    tampered_token = f"{header}.{payload}.{replacement}{signature[1:]}"

    with pytest.raises(JWTError):
        JWTManager.decode_token(tampered_token)

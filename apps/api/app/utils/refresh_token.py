from __future__ import annotations

import hashlib
import hmac

from app.core.config import settings


def hash_refresh_token(token: str) -> str:
    """
    Deterministically hash a refresh token.

    The raw refresh token is never stored in the database.
    """

    return hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

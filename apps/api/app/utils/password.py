from __future__ import annotations

import bcrypt


# ==========================================================
# Password Utilities
# ==========================================================


class PasswordManager:
    """
    Handles password hashing and verification using bcrypt.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generate a secure bcrypt hash. Truncate to 72 bytes as per bcrypt spec.
        """
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """
        Verify a plain password against its bcrypt hash.
        """
        try:
            pwd_bytes = plain_password.encode("utf-8")[:72]
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Determine whether an existing hash should be upgraded.
        """
        return False

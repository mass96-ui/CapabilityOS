from __future__ import annotations

import secrets


class OTPManager:
    """Secure OTP generation and verification utilities."""

    OTP_LENGTH = 6

    @staticmethod
    def generate_otp() -> str:
        """Generate a cryptographically secure 6-digit OTP."""
        return f"{secrets.randbelow(1_000_000):06d}"
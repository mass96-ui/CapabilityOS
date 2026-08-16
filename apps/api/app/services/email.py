from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    """Email delivery service for CapabilityOS."""

    @staticmethod
    async def send_verification_otp(
        email: str,
        otp: str,
        first_name: str | None = None,
    ) -> None:
        """Send the email verification OTP."""

        message = EmailMessage()

        message["Subject"] = "CapabilityOS Email Verification"
        message["From"] = (
            settings.SMTP_USERNAME
            or "no-reply@capabilityos.dev"
        )
        message["To"] = email

        greeting = (
            f"Hello {first_name}," if first_name else "Hello,"
        )

        message.set_content(
            f"""
{greeting}

Welcome to CapabilityOS.

Your email verification OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not create a CapabilityOS account, you can safely ignore this email.

Regards,
CapabilityOS Team
""".strip()
        )

        await asyncio.to_thread(
            EmailService._send,
            message,
        )

    @staticmethod
    def _send(message: EmailMessage) -> None:
        """Synchronous SMTP delivery executed in a worker thread."""

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=10,
        ) as server:

            if settings.SMTP_TLS:
                server.starttls()

            if settings.SMTP_USERNAME:
                server.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD,
                )

            server.send_message(message)

    @staticmethod
    async def _send_raw(
        email: str,
        subject: str,
        body: str,
    ) -> None:
        """Send a plain-text email."""

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = (
            settings.SMTP_USERNAME
            or "no-reply@capabilityos.dev"
        )
        message["To"] = email
        message.set_content(body)

        await asyncio.to_thread(EmailService._send, message)
from __future__ import annotations

import re

from pydantic import EmailStr

# ==========================================================
# Username Validation
# ==========================================================


USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,50}$")


def validate_username(username: str) -> str:
    """
    Validate username format.

    Rules:
    - 3 to 50 characters
    - letters
    - numbers
    - underscore
    - hyphen
    - dot
    """

    username = username.strip()

    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "Username must contain only letters, numbers, '_', '-', or '.'"
        )

    return username


# ==========================================================
# Password Validation
# ==========================================================


UPPERCASE = re.compile(r"[A-Z]")
LOWERCASE = re.compile(r"[a-z]")
NUMBER = re.compile(r"\d")
SPECIAL = re.compile(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]")


def validate_password(password: str) -> str:
    """
    Validate password strength.

    Rules:
    - minimum 8 characters
    - uppercase
    - lowercase
    - number
    - special character
    """

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    if not UPPERCASE.search(password):
        raise ValueError(
            "Password must contain an uppercase letter."
        )

    if not LOWERCASE.search(password):
        raise ValueError(
            "Password must contain a lowercase letter."
        )

    if not NUMBER.search(password):
        raise ValueError(
            "Password must contain a number."
        )

    if not SPECIAL.search(password):
        raise ValueError(
            "Password must contain a special character."
        )

    return password


# ==========================================================
# Email Validation
# ==========================================================


def validate_email(email: str) -> str:
    """
    Normalize email.
    """

    return str(EmailStr(email)).lower()


# ==========================================================
# Name Validation
# ==========================================================


NAME_PATTERN = re.compile(r"^[A-Za-z ]{2,100}$")


def validate_name(name: str) -> str:
    """
    Validate person names.
    """

    name = name.strip()

    if not NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Invalid name."
        )

    return name


# ==========================================================
# UUID Validation
# ==========================================================


UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


def validate_uuid(value: str) -> str:
    """
    Validate UUID string.
    """

    if not UUID_PATTERN.fullmatch(value):
        raise ValueError(
            "Invalid UUID."
        )

    return value
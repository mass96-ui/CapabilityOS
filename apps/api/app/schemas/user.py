from __future__ import annotations

from typing import Optional
from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema


class UserBase(BaseSchema):
    """
    Base user properties shared across request schemas.
    """

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    is_superuser: bool = Field(default=False, description="Superuser status")


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """

    password: str = Field(..., min_length=8, max_length=128, description="Plaintext password")


class UserUpdate(BaseSchema):
    """
    Schema for updating user details.
    """

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(default=None)


class UserResponse(UUIDSchema, TimestampSchema):
    """
    Public user representation returned in API responses.
    """

    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool

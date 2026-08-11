from __future__ import annotations

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ==========================================================
# Base Schema
# ==========================================================


class BaseSchema(BaseModel):
    """
    Base schema for all request/response models.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


# ==========================================================
# Timestamp Schema
# ==========================================================


class TimestampSchema(BaseSchema):
    """
    Adds audit timestamps to response models.
    """

    created_at: datetime
    updated_at: datetime


# ==========================================================
# UUID Schema
# ==========================================================


class UUIDSchema(BaseSchema):
    """
    Common UUID identifier schema.
    """

    id: str = Field(..., description="Resource UUID")


# ==========================================================
# Standard API Response
# ==========================================================


class APIResponse(BaseSchema, Generic[T]):
    """
    Generic API response wrapper.
    """

    success: bool = True
    message: str = "Success"
    data: Optional[T] = None


# ==========================================================
# Pagination Request
# ==========================================================


class PaginationParams(BaseSchema):
    """
    Standard pagination query parameters.
    """

    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page",
    )


# ==========================================================
# Pagination Metadata
# ==========================================================


class PaginationMeta(BaseSchema):
    """
    Pagination metadata returned with paginated responses.
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int


# ==========================================================
# Paginated Response
# ==========================================================


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Standard paginated API response.
    """

    success: bool = True
    message: str = "Success"
    items: list[T]
    meta: PaginationMeta


# ==========================================================
# Health Response
# ==========================================================


class HealthResponse(BaseSchema):
    """
    Health check response.
    """

    status: str
    version: str
    environment: str


# ==========================================================
# Error Response
# ==========================================================


class ErrorResponse(BaseSchema):
    """
    Standard API error response.
    """

    success: bool = False
    detail: str
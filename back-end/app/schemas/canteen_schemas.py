"""Pydantic schemas for the canteen domain."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BusinessHoursEntry(BaseModel):
    """One persisted operating-hours range."""

    day: Literal["weekdays", "saturday", "sunday"]
    opens_at: str = Field(..., pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    closes_at: str = Field(..., pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    is_open: bool


class CanteenBase(BaseModel):
    """Common canteen attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    location: str = Field(..., min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    logo_url: str | None = Field(default=None, max_length=500, pattern=r"^https?://")
    is_open: bool = False
    opening_hours: list[BusinessHoursEntry] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")
    @field_validator("name", "location")
    @classmethod
    def validate_identity_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Canteen name and location must contain at least 2 characters")
        return cleaned


class CanteenCreate(CanteenBase):
    """Attributes required to create a canteen."""

    user_id: UUID


class CanteenUpdate(BaseModel):
    """Optional attributes for partial canteen updates."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    location: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    logo_url: Optional[str] = Field(default=None, max_length=500, pattern=r"^https?://")
    is_open: Optional[bool] = None
    opening_hours: Optional[list[BusinessHoursEntry]] = None
    model_config = ConfigDict(extra="forbid")
    @field_validator("name", "location")
    @classmethod
    def validate_identity_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Canteen name and location must contain at least 2 characters")
        return cleaned


class CanteenResponse(CanteenBase):
    """Canteen output schema."""

    id: UUID
    user_id: UUID
    products: list[UUID] = Field(default_factory=list)
    is_accepting_orders: bool = False
    next_opening_at: datetime | None = None
    commercial_terms_accepted_at: datetime | None = None
    moderation_status: Literal["pending", "approved", "rejected"] = "pending"
    moderation_reviewed_at: datetime | None = None
    rejection_reason: str | None = None
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CanteenOnboarding(BaseModel):
    """Commercial profile submitted by the authenticated canteen staff."""

    model_config = ConfigDict(extra="forbid")
    description: str = Field(..., min_length=20, max_length=1000)
    logo_url: str = Field(..., max_length=500, pattern=r"^https?://")
    accepted_commercial_terms: Literal[True]

    @field_validator("description", "logo_url")
    @classmethod
    def strip_onboarding_fields(cls, value: str) -> str:
        return value.strip()


class CanteenModerationUpdate(BaseModel):
    """Explicit decision available only to administrators."""

    model_config = ConfigDict(extra="forbid")
    status: Literal["approved", "rejected"]
    rejection_reason: str | None = Field(default=None, min_length=5, max_length=500)

    @field_validator("rejection_reason")
    @classmethod
    def strip_rejection_reason(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


SchemaBase = CanteenBase
SchemaCreate = CanteenCreate
SchemaUpdate = CanteenUpdate
SchemaResponse = CanteenResponse

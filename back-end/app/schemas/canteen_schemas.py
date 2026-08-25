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
    model_config = ConfigDict(from_attributes=True, extra="forbid")


SchemaBase = CanteenBase
SchemaCreate = CanteenCreate
SchemaUpdate = CanteenUpdate
SchemaResponse = CanteenResponse

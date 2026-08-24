"""Pydantic schemas for the canteen domain."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CanteenBase(BaseModel):
    """Common canteen attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    location: str = Field(..., min_length=2, max_length=200)
    is_open: bool = False
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
    model_config = ConfigDict(from_attributes=True, extra="forbid")


SchemaBase = CanteenBase
SchemaCreate = CanteenCreate
SchemaUpdate = CanteenUpdate
SchemaResponse = CanteenResponse

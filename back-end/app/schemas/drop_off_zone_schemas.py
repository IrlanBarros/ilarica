"""Pydantic schemas for the drop-off zone domain."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DropOffZoneBase(BaseModel):
    """Common drop-off zone attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    capacity_total: int = Field(..., gt=0)
    current_load: int = Field(default=0, ge=0)
    is_active: bool = False

    @field_validator("current_load")
    @classmethod
    def validate_current_load(cls, value: int) -> int:
        if value < 0:
            raise ValueError("current_load cannot be negative")
        return value


class DropOffZoneCreate(DropOffZoneBase):
    """Attributes required to create a drop-off zone."""


class DropOffZoneUpdate(BaseModel):
    """Optional attributes for partial updates."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    capacity_total: Optional[int] = Field(default=None, gt=0)
    current_load: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class DropOffZoneResponse(DropOffZoneBase):
    """Drop-off zone output schema."""

    id: str
    model_config = ConfigDict(from_attributes=True)


SchemaBase = DropOffZoneBase
SchemaCreate = DropOffZoneCreate
SchemaUpdate = DropOffZoneUpdate
SchemaResponse = DropOffZoneResponse

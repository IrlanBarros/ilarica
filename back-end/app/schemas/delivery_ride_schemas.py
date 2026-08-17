"""Pydantic schemas for the delivery ride domain."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeliveryRideBase(BaseModel):
    """Common delivery ride attributes."""

    drop_off_zone_id: str = Field(..., min_length=1)
    status: str = Field(default="draft", min_length=2, max_length=50)
    assigned_courier_id: Optional[str] = None
    is_arrived: bool = False

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"draft", "queued", "accepted", "arrived", "completed"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("status must be one of: draft, queued, accepted, arrived, completed")
        return normalized


class DeliveryRideCreate(DeliveryRideBase):
    """Attributes required to create a delivery ride."""


class DeliveryRideUpdate(BaseModel):
    """Optional attributes for partial updates."""

    drop_off_zone_id: Optional[str] = Field(default=None, min_length=1)
    status: Optional[str] = Field(default=None, min_length=2, max_length=50)
    assigned_courier_id: Optional[str] = None
    is_arrived: Optional[bool] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {"draft", "queued", "accepted", "arrived", "completed"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("status must be one of: draft, queued, accepted, arrived, completed")
        return normalized


class DeliveryRideResponse(DeliveryRideBase):
    """Delivery ride output schema."""

    id: str
    model_config = ConfigDict(from_attributes=True)


SchemaBase = DeliveryRideBase
SchemaCreate = DeliveryRideCreate
SchemaUpdate = DeliveryRideUpdate
SchemaResponse = DeliveryRideResponse

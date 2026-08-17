"""Pydantic schemas for transport kits."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransportKitBase(BaseModel):
    """Common transport kit attributes."""

    serial_number: str = Field(..., min_length=3, max_length=60)
    is_allocated: bool = False
    courier_id: Optional[str] = None


class TransportKitCreate(TransportKitBase):
    """Attributes required to create a transport kit."""


class TransportKitUpdate(BaseModel):
    """Optional attributes for partial updates."""

    serial_number: Optional[str] = Field(default=None, min_length=3, max_length=60)
    is_allocated: Optional[bool] = None
    courier_id: Optional[str] = None


class TransportKitResponse(TransportKitBase):
    """Transport kit output schema."""

    id: str
    model_config = ConfigDict(from_attributes=True)


SchemaBase = TransportKitBase
SchemaCreate = TransportKitCreate
SchemaUpdate = TransportKitUpdate
SchemaResponse = TransportKitResponse

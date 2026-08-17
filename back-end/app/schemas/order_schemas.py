"""Pydantic schemas for orders and order items."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderItemBase(BaseModel):
    """Common order item attributes."""

    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Quantity must be greater than zero")
        return value


class OrderItemCreate(OrderItemBase):
    """Order item creation data."""


class OrderItemUpdate(BaseModel):
    """Partial order item updates."""

    product_id: Optional[str] = Field(default=None, min_length=1)
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[Decimal] = Field(default=None, gt=0)


class OrderItemResponse(OrderItemBase):
    """Order item output model."""

    id: str
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Common order attributes."""

    customer_id: str = Field(..., min_length=1)
    canteen_id: str = Field(..., min_length=1)
    drop_off_zone_id: str = Field(..., min_length=1)
    status: str = Field(default="draft", min_length=2, max_length=50)
    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class OrderCreate(OrderBase):
    """Required attributes to create an order."""

    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    """Optional attributes for partial updates."""

    status: Optional[str] = Field(default=None, min_length=2, max_length=50)
    total_amount: Optional[Decimal] = Field(default=None, ge=0)
    pickup_pin: Optional[str] = Field(default=None, min_length=4, max_length=4)

    @field_validator("pickup_pin")
    @classmethod
    def validate_pickup_pin(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.isdigit() or len(value) != 4:
            raise ValueError("Pickup pin must be a 4-digit numeric string")
        return value


class OrderResponse(OrderBase):
    """Order output schema."""

    id: str
    items: List[OrderItemResponse] = []
    pickup_pin: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


SchemaBase = OrderBase
SchemaCreate = OrderCreate
SchemaUpdate = OrderUpdate
SchemaResponse = OrderResponse

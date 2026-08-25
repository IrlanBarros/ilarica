"""Pydantic schemas for orders and order items."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

FulfillmentType = Literal["pickup", "delivery"]


def _normalize_location_details(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


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


class OrderItemCreate(BaseModel):
    """Client-provided item data; prices are resolved by the server."""

    model_config = ConfigDict(extra="forbid")
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


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
    fulfillment_type: FulfillmentType = "delivery"
    drop_off_zone_id: Optional[str] = Field(default=None, min_length=1)
    location_details: Optional[str] = Field(default=None, max_length=180)
    status: str = Field(default="draft", min_length=2, max_length=50)
    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("location_details")
    @classmethod
    def validate_location_details(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_location_details(value)


class OrderCreate(BaseModel):
    """Required attributes to create an order."""

    model_config = ConfigDict(extra="forbid")
    customer_id: str = Field(..., min_length=1)
    canteen_id: str = Field(..., min_length=1)
    fulfillment_type: FulfillmentType = "delivery"
    drop_off_zone_id: Optional[str] = Field(default=None, min_length=1)
    location_details: Optional[str] = Field(default=None, max_length=180)
    items: List[OrderItemCreate] = Field(..., min_length=1)

    @field_validator("location_details")
    @classmethod
    def validate_location_details(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_location_details(value)

    @model_validator(mode="after")
    def validate_fulfillment(self) -> "OrderCreate":
        if self.fulfillment_type == "delivery" and not self.drop_off_zone_id:
            raise ValueError("A drop-off zone is required for delivery")
        if self.fulfillment_type == "pickup" and self.drop_off_zone_id is not None:
            raise ValueError("Pickup orders must not include a drop-off zone")
        return self


class OrderUpdate(BaseModel):
    """Optional attributes for partial updates."""

    model_config = ConfigDict(extra="forbid")

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


class SellerOrderStatusUpdate(BaseModel):
    """Explicit next status requested by the authenticated canteen staff."""

    model_config = ConfigDict(extra="forbid")
    status: Literal["preparing", "ready_for_pickup"]


class SellerPickupConfirmation(BaseModel):
    """Customer-provided PIN used by the owning canteen at pickup."""

    model_config = ConfigDict(extra="forbid")
    pickup_pin: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")


class SellerPickupConfirmationResponse(BaseModel):
    id: UUID
    status: Literal["completed"]


class SellerOrderCustomerResponse(BaseModel):
    """Minimum customer identity required to prepare an order."""

    id: UUID
    name: str


class SellerOrderDestinationResponse(BaseModel):
    """Minimum delivery destination required by the canteen operation."""

    id: UUID
    name: str
    description: Optional[str] = None


class SellerOrderItemResponse(BaseModel):
    """Server-priced order item displayed in the seller dashboard."""

    id: UUID
    product_id: UUID
    name: str
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)


class SellerOrderResponse(BaseModel):
    """Canteen-scoped order projection for operational use."""

    id: UUID
    canteen_id: UUID
    status: Literal["paid", "preparing", "ready_for_pickup", "completed"]
    items: List[SellerOrderItemResponse]
    total_amount: Decimal = Field(..., ge=0)
    customer: SellerOrderCustomerResponse
    fulfillment_type: FulfillmentType
    destination: Optional[SellerOrderDestinationResponse] = None
    location_details: Optional[str] = None


class CustomerOrderCanteenResponse(BaseModel):
    id: UUID
    name: str
    location: str


class CustomerOrderResponse(BaseModel):
    id: UUID
    canteen_id: UUID
    status: str
    fulfillment_type: FulfillmentType
    items: List[SellerOrderItemResponse]
    total_amount: Decimal = Field(..., ge=0)
    destination: Optional[SellerOrderDestinationResponse] = None
    location_details: Optional[str] = None
    canteen: CustomerOrderCanteenResponse
    pickup_pin: Optional[str] = None


SchemaBase = OrderBase
SchemaCreate = OrderCreate
SchemaUpdate = OrderUpdate
SchemaResponse = OrderResponse

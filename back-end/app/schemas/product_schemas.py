"""Pydantic schemas for the catalog product domain."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    """Common product attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    is_active: bool = True

    @field_validator("price")
    @classmethod
    def validate_positive_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Price must be greater than zero")
        return value


class ProductCreate(ProductBase):
    """Required attributes to create a product."""

    canteen_id: str = Field(..., min_length=1)


class ProductUpdate(BaseModel):
    """Optional attributes for partial product updates."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    is_active: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def validate_positive_price(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("Price must be greater than zero")
        return value


class ProductResponse(ProductBase):
    """Product output schema."""

    id: str
    canteen_id: str
    is_fast_stock_enabled: bool = False
    model_config = ConfigDict(from_attributes=True)


SchemaBase = ProductBase
SchemaCreate = ProductCreate
SchemaUpdate = ProductUpdate
SchemaResponse = ProductResponse

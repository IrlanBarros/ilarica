"""Pydantic schemas for the canteen domain."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CanteenBase(BaseModel):
    """Common canteen attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    location: str = Field(..., min_length=2, max_length=200)
    is_open: bool = False
    products: list[str] = Field(default_factory=list)

    @field_validator("products")
    @classmethod
    def validate_products(cls, value: list[str]) -> list[str]:
        return [product.strip() for product in value if product and product.strip()]


class CanteenCreate(CanteenBase):
    """Attributes required to create a canteen."""

    user_id: str = Field(..., min_length=1)


class CanteenUpdate(BaseModel):
    """Optional attributes for partial canteen updates."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    location: Optional[str] = Field(default=None, min_length=2, max_length=200)
    is_open: Optional[bool] = None
    products: Optional[list[str]] = None

    @field_validator("products")
    @classmethod
    def validate_products(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value
        return [product.strip() for product in value if product and product.strip()]


class CanteenResponse(CanteenBase):
    """Canteen output schema."""

    id: str
    user_id: str
    model_config = ConfigDict(from_attributes=True)


SchemaBase = CanteenBase
SchemaCreate = CanteenCreate
SchemaUpdate = CanteenUpdate
SchemaResponse = CanteenResponse

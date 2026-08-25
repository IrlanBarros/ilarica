"""Pydantic schemas for the catalog product domain."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProductCategory = Literal["salgados", "bebidas", "refeicoes", "doces", "outros"]


class ProductBase(BaseModel):
    """Common product attributes."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    image_url: Optional[str] = Field(default=None, max_length=500)
    category: ProductCategory = "outros"
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0, le=100_000)
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

    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None
    image_url: Optional[str] = Field(default=None, max_length=500)
    category: Optional[ProductCategory] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0, le=100_000)
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

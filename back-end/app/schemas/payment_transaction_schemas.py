"""Pydantic schemas for payment transactions."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaymentTransactionBase(BaseModel):
    """Common payment transaction attributes."""

    order_id: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., min_length=2, max_length=50)
    status: str = Field(default="pending", min_length=2, max_length=30)
    external_reference: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("amount must be greater than zero")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"pending", "processing", "succeeded", "failed"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("status must be one of: pending, processing, succeeded, failed")
        return normalized


class PaymentTransactionCreate(PaymentTransactionBase):
    """Attributes required to create a payment transaction."""


class PaymentTransactionUpdate(BaseModel):
    """Optional attributes for partial updates."""

    order_id: Optional[str] = Field(default=None, min_length=1)
    amount: Optional[Decimal] = Field(default=None, gt=0)
    payment_method: Optional[str] = Field(default=None, min_length=2, max_length=50)
    status: Optional[str] = Field(default=None, min_length=2, max_length=30)
    external_reference: Optional[str] = None


class PaymentTransactionResponse(PaymentTransactionBase):
    """Payment transaction output schema."""

    id: str
    model_config = ConfigDict(from_attributes=True)


SchemaBase = PaymentTransactionBase
SchemaCreate = PaymentTransactionCreate
SchemaUpdate = PaymentTransactionUpdate
SchemaResponse = PaymentTransactionResponse

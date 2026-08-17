"""Pydantic schemas for wallet operations."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WalletBase(BaseModel):
    """Common wallet attributes."""

    user_id: str = Field(..., min_length=1)
    balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    pending_withdrawal: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("balance", "pending_withdrawal")
    @classmethod
    def validate_money(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("Monetary values cannot be negative")
        return value


class WalletCreate(WalletBase):
    """Required attributes to create a wallet."""


class WalletUpdate(BaseModel):
    """Optional wallet fields."""

    balance: Optional[Decimal] = Field(default=None, ge=0)
    pending_withdrawal: Optional[Decimal] = Field(default=None, ge=0)


class WalletResponse(WalletBase):
    """Wallet output schema."""

    id: str
    model_config = ConfigDict(from_attributes=True)


SchemaBase = WalletBase
SchemaCreate = WalletCreate
SchemaUpdate = WalletUpdate
SchemaResponse = WalletResponse

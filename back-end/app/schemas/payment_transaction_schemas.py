"""Public contracts for secure payment intents."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaymentMethod = Literal["pix", "wallet"]
PaymentStatus = Literal["pending", "processing", "succeeded", "failed", "expired"]


class PaymentIntentCreate(BaseModel):
    """Only payment intent data the authenticated customer may choose."""

    model_config = ConfigDict(extra="forbid")
    order_id: str = Field(..., min_length=1)
    payment_method: PaymentMethod


class PaymentWebhookUpdate(BaseModel):
    """Provider-only payment result payload."""

    model_config = ConfigDict(extra="forbid")
    status: Literal["succeeded", "failed"]
    external_reference: str | None = Field(default=None, max_length=255)
    failure_reason: str | None = Field(default=None, max_length=255)


class EfiPixNotification(BaseModel):
    """Minimal webhook hint; all financial fields are ignored in favor of active verification."""

    model_config = ConfigDict(extra="allow")
    txid: str = Field(..., min_length=26, max_length=35, pattern=r"^[A-Za-z0-9]+$")


class EfiPixWebhook(BaseModel):
    """Efí callback envelope."""

    model_config = ConfigDict(extra="allow")
    pix: list[EfiPixNotification] = Field(default_factory=list, max_length=100)


class PaymentTransactionResponse(BaseModel):
    """Safe payment intent state returned to its owner."""

    id: str
    order_id: str
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    external_reference: str | None = None
    pix_copy_paste: str | None = None
    pix_qr_code: str | None = None
    expires_at: datetime | None = None
    failure_reason: str | None = None
    created_at: datetime
    confirmed_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# Compatibility alias for internal imports while the public contract remains intent-only.
PaymentTransactionCreate = PaymentIntentCreate

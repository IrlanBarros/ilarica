"""Financial and remuneration context: payment transaction entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from app.domain.exceptions import (
    InvalidAmountError,
    PaymentAlreadyProcessedError,
    PaymentTransactionFailedError,
)


@dataclass
class PaymentTransaction:
    """Entity representing a payment attempt for an order."""

    id: str
    order_id: str
    amount: Decimal
    payment_method: str
    status: str = "pending"
    transaction_reference: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    failure_reason: str | None = None

    def processPayment(self) -> str:
        """Start the payment workflow for the order."""
        if self.amount <= Decimal("0"):
            raise InvalidAmountError("The payment amount must be greater than zero.")
        if self.status in {"processing", "succeeded", "failed"}:
            raise PaymentAlreadyProcessedError("This payment transaction has already been processed.")

        self.status = "processing"
        return self.status

    def confirmSuccess(self) -> str:
        """Confirm the payment transaction successfully completed."""
        if self.status == "failed":
            raise PaymentTransactionFailedError("This payment transaction has failed and cannot be confirmed as successful.")
        if self.status == "succeeded":
            return self.status

        self.status = "succeeded"
        return self.status

    def failTransaction(self, reason: str) -> str:
        """Mark the payment transaction as failed with a business reason."""
        if not reason or not reason.strip():
            raise ValueError("A failure reason is required when declining a payment.")

        self.status = "failed"
        self.failure_reason = reason.strip()
        return self.status

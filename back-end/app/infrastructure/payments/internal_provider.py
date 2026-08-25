"""Deterministic local Pix provider used only in development and automated tests."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.application.ports.payment_provider import PaymentProvider, PixCharge, PixChargeStatus


class InternalPixProvider(PaymentProvider):
    name = "internal"

    def create_pix_charge(
        self, *, reference: str, amount: Decimal, expiration_seconds: int, order_id: str
    ) -> PixCharge:
        return PixCharge(
            reference=reference,
            copy_paste=f"ILARICA-SANDBOX|order={order_id}|amount={amount:.2f}|reference={reference}",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds),
        )

    def get_pix_charge(self, reference: str) -> PixChargeStatus:
        return PixChargeStatus(reference=reference, status="pending")

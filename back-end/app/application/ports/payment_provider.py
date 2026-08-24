"""Port implemented by external Pix payment providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class PixCharge:
    """Provider-neutral result of creating a Pix charge."""

    reference: str
    copy_paste: str
    expires_at: datetime


@dataclass(frozen=True)
class PixChargeStatus:
    """Provider-neutral state used by webhook verification and reconciliation."""

    reference: str
    status: str
    paid_amount: Decimal | None = None


class PaymentProvider(ABC):
    """External Pix boundary; it owns no iLarica business decisions or persistence."""

    name: str

    @abstractmethod
    def create_pix_charge(
        self, *, reference: str, amount: Decimal, expiration_seconds: int, order_id: str
    ) -> PixCharge:
        """Create or replay a provider charge using a deterministic reference."""

    @abstractmethod
    def get_pix_charge(self, reference: str) -> PixChargeStatus:
        """Read authoritative provider state without mutating the local order."""

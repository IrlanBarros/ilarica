"""Order context: value object for order items."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderItem:
    """Immutable value object representing a single product in an order."""

    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Order item quantity must be greater than zero.")
        if self.unit_price < Decimal("0"):
            raise ValueError("Order item unit price cannot be negative.")

    def calculateSubtotal(self) -> Decimal:
        """Return the subtotal for the item."""
        return self.unit_price * self.quantity

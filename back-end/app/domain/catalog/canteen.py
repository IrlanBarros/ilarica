"""Catalog context: canteen aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.exceptions import CanteenAlreadyClosedError, CanteenAlreadyOpenError


@dataclass
class Canteen:
    """Aggregate root representing a campus canteen."""

    id: str
    user_id: str
    name: str
    location: str
    is_open: bool = False
    products: list[str] = field(default_factory=list)
    opening_hours: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize and validate the persisted canteen identity."""
        self.name = self.name.strip()
        self.location = self.location.strip()
        if len(self.name) < 2:
            raise ValueError("Canteen name must contain at least 2 characters.")
        if len(self.location) < 2:
            raise ValueError("Canteen location must contain at least 2 characters.")

    def update_profile(self, *, name: str | None = None, location: str | None = None) -> None:
        """Update identifying fields without allowing blank persisted values."""
        next_name = self.name if name is None else name.strip()
        next_location = self.location if location is None else location.strip()
        if len(next_name) < 2:
            raise ValueError("Canteen name must contain at least 2 characters.")
        if len(next_location) < 2:
            raise ValueError("Canteen location must contain at least 2 characters.")
        self.name = next_name
        self.location = next_location

    def openOperation(self) -> bool:
        """Open the canteen for a service operation."""
        if self.is_open:
            raise CanteenAlreadyOpenError("The canteen is already open.")

        self.is_open = True
        return True

    def closeOperation(self) -> bool:
        """Close the canteen for a service operation."""
        if not self.is_open:
            raise CanteenAlreadyClosedError("The canteen is already closed.")

        self.is_open = False
        return True

    def addProduct(self, product_id: str) -> None:
        """Register a product in the canteen catalog."""
        if product_id not in self.products:
            self.products.append(product_id)

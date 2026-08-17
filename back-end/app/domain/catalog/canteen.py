"""Catalog context: canteen aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.exceptions import CanteenAlreadyClosedError, CanteenAlreadyOpenError


@dataclass
class Canteen:
    """Aggregate root representing a campus canteen."""

    id: str
    name: str
    is_open: bool = False
    location: str = ""
    products: list[str] = field(default_factory=list)

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

"""Catalog context: product entity."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.exceptions import ProductAlreadyDisabledError, ProductAlreadyEnabledError


@dataclass
class Product:
    """Entity representing a sellable product."""

    id: str
    name: str
    price: Decimal
    is_active: bool = True
    stock_quantity: int = 0
    is_fast_stock_enabled: bool = False
    canteen_id: str | None = None
    description: str | None = None
    image_url: str | None = None

    def enableFastStock(self) -> bool:
        """Enable a fast-stock mode for the product."""
        if self.is_fast_stock_enabled:
            raise ProductAlreadyEnabledError("Fast stock is already enabled for this product.")

        self.is_fast_stock_enabled = True
        return True

    def disableProduct(self) -> bool:
        """Disable the product so it cannot be sold."""
        if not self.is_active:
            raise ProductAlreadyDisabledError("The product is already disabled.")

        self.is_active = False
        self.is_fast_stock_enabled = False
        return True

    def addStock(self, quantity: int) -> int:
        """Increase the available stock."""
        if quantity <= 0:
            raise ValueError("Stock quantity must be greater than zero.")
        self.stock_quantity += quantity
        return self.stock_quantity

    def reserveStock(self, quantity: int) -> int:
        """Reserve stock for an order."""
        if quantity <= 0:
            raise ValueError("Reservation quantity must be greater than zero.")
        if quantity > self.stock_quantity:
            raise ValueError("Not enough stock available for this reservation.")

        self.stock_quantity -= quantity
        return self.stock_quantity

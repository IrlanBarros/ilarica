"""Use case for toggling fast stock status on a product."""

from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.repositories import IProductRepository
from app.domain.catalog.product import Product


@dataclass
class ToggleFastStockUseCase:
    """Toggle the fast-stock availability of a product."""

    product_repository: IProductRepository

    def execute(self, product_id: str) -> Product:
        """Flip fast stock status and persist the product."""
        if not product_id:
            raise ValueError("A valid product identifier is required.")

        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ValueError("The product does not exist.")

        if product.is_fast_stock_enabled:
            product.is_fast_stock_enabled = False
        else:
            product.enableFastStock()

        return self.product_repository.save(product)

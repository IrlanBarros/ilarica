"""Business services for product-related operations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from app.application.ports.repositories import IProductRepository
from app.domain.catalog.product import Product


@dataclass
class ProductService:
    """Encapsulates product-related business rules."""

    product_repo: IProductRepository

    def get(self, product_id: str) -> Product | None:
        return self.product_repo.get_by_id(product_id)

    def create(self, product: Product) -> Product:
        # Validation: name and price
        if not product.name or product.price <= 0:
            raise ValueError("Product must have a name and a positive price")
        return self.product_repo.save(product)

    def enable_fast_stock(self, product_id: str) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")
        product.enableFastStock()
        return self.product_repo.save(product)

    def list_by_ids(self, ids: Iterable[str]) -> List[Product]:
        return self.product_repo.list_by_ids(ids)

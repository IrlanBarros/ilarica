from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.use_cases.toggle_fast_stock import ToggleFastStockUseCase
from app.domain.catalog.product import Product


@pytest.fixture
def product() -> Product:
    return Product(id="p-1", name="Sandwich", price=Decimal("18.00"), stock_quantity=5, is_active=True)


def test_toggle_fast_stock_use_case_enables_fast_stock(product: Product) -> None:
    # Arrange
    product_repository = MagicMock()
    product_repository.get_by_id.return_value = product
    product_repository.save.side_effect = lambda updated_product: updated_product
    use_case = ToggleFastStockUseCase(product_repository)

    # Act
    result = use_case.execute("p-1")

    # Assert
    assert result.is_fast_stock_enabled is True
    product_repository.save.assert_called_once_with(product)


def test_toggle_fast_stock_use_case_disables_fast_stock_when_already_enabled(product: Product) -> None:
    # Arrange
    product.is_fast_stock_enabled = True
    product_repository = MagicMock()
    product_repository.get_by_id.return_value = product
    product_repository.save.side_effect = lambda updated_product: updated_product
    use_case = ToggleFastStockUseCase(product_repository)

    # Act
    result = use_case.execute("p-1")

    # Assert
    assert result.is_fast_stock_enabled is False
    product_repository.save.assert_called_once_with(product)

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.use_cases.confirm_pickup_and_complete import ConfirmPickupAndCompleteUseCase
from app.domain.exceptions import InvalidPinError
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


@pytest.fixture
def order() -> Order:
    item = OrderItem(
        product_id="p-1",
        product_name="Rice Bowl",
        quantity=1,
        unit_price=Decimal("12.50"),
    )
    order = Order(
        id="order-1",
        user_id="user-1",
        items=[item],
        status=Order.STATUS_READY_FOR_PICKUP,
        is_paid=True,
    )
    order.pickup_pin = "1234"
    return order


@pytest.fixture
def wallet_repository() -> MagicMock:
    return MagicMock()


def test_confirm_pickup_and_complete_use_case_completes_order_and_credits_wallet(
    order: Order,
    wallet_repository: MagicMock,
) -> None:
    # Arrange
    order_repository = MagicMock()
    order_repository.get_by_id.return_value = order
    wallet = MagicMock(balance=Decimal("0.00"))
    wallet_repository.get_by_user_id.return_value = wallet
    use_case = ConfirmPickupAndCompleteUseCase(order_repository, wallet_repository, Decimal("8.50"))

    # Act
    result = use_case.execute("order-1", "courier-1", "1234")

    # Assert
    assert result.status == Order.STATUS_COMPLETED
    assert order.is_paid is True
    wallet.creditDeliveryFee.assert_called_once_with(Decimal("8.50"))
    wallet_repository.save.assert_called_once_with(wallet)
    order_repository.save.assert_called_once_with(order)


def test_confirm_pickup_and_complete_use_case_rejects_missing_order(
    wallet_repository: MagicMock,
) -> None:
    # Arrange
    order_repository = MagicMock()
    order_repository.get_by_id.return_value = None
    use_case = ConfirmPickupAndCompleteUseCase(order_repository, wallet_repository)

    # Act / Assert
    with pytest.raises(ValueError, match="order does not exist"):
        use_case.execute("order-404", "courier-1", "1234")


def test_confirm_pickup_and_complete_use_case_rejects_wrong_pin(
    order: Order,
    wallet_repository: MagicMock,
) -> None:
    # Arrange
    order_repository = MagicMock()
    order_repository.get_by_id.return_value = order
    use_case = ConfirmPickupAndCompleteUseCase(order_repository, wallet_repository)

    # Act / Assert
    with pytest.raises(InvalidPinError):
        use_case.execute("order-1", "courier-1", "9999")
    wallet_repository.save.assert_not_called()

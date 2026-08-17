from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.use_cases.accept_delivery import AcceptDeliveryUseCase
from app.domain.logistics.delivery_ride import DeliveryRide
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def delivery_ride() -> DeliveryRide:
    return DeliveryRide(id="ride-1", order_id="order-1")


@pytest.fixture
def paid_order() -> Order:
    item = OrderItem(
        product_id="p-1",
        product_name="Rice Bowl",
        quantity=1,
        unit_price=Decimal("12.50"),
    )
    return Order(id="order-1", user_id="user-1", items=[item], status=Order.STATUS_PAID, is_paid=True)


def test_accept_delivery_use_case_assigns_courier_and_dispatches_order(
    session: MagicMock,
    delivery_ride: DeliveryRide,
    paid_order: Order,
) -> None:
    ride_repository = MagicMock()
    order_repository = MagicMock()
    ride_repository.get_by_id.return_value = delivery_ride
    ride_repository.save.side_effect = lambda ride: ride
    order_repository.get_by_id.return_value = paid_order
    order_repository.save.side_effect = lambda order: order

    use_case = AcceptDeliveryUseCase(
        session=session,
        delivery_ride_repository=ride_repository,
        order_repository=order_repository,
    )

    result = use_case.execute("ride-1", "courier-1")

    assert result.assigned_courier_id == "courier-1"
    assert result.status == "in_transit"
    assert paid_order.delivery_ride_id == "ride-1"
    assert paid_order.status == Order.STATUS_IN_TRANSIT
    ride_repository.save.assert_called_once_with(delivery_ride)
    order_repository.save.assert_called_once_with(paid_order)
    session.commit.assert_called_once_with()


def test_accept_delivery_use_case_rejects_missing_ride(session: MagicMock) -> None:
    ride_repository = MagicMock()
    order_repository = MagicMock()
    ride_repository.get_by_id.return_value = None
    use_case = AcceptDeliveryUseCase(
        session=session,
        delivery_ride_repository=ride_repository,
        order_repository=order_repository,
    )

    with pytest.raises(ValueError, match="delivery ride does not exist"):
        use_case.execute("ride-404", "courier-1")

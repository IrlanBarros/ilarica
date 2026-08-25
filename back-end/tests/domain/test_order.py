from __future__ import annotations

import pytest

from app.domain.exceptions import InvalidOrderStatusTransitionError, InvalidPinError, OrderAlreadyPaidError, OrderNotPaidError
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


@pytest.fixture
def order() -> Order:
    item = OrderItem(
        product_id="p-1",
        product_name="Rice Bowl",
        quantity=2,
        unit_price=12.50,
    )
    return Order(id="order-1", user_id="user-1", items=[item])


def test_order_can_confirm_payment_and_generate_pickup_pin(order: Order) -> None:
    # Arrange
    assert order.is_paid is False

    # Act
    order.startCheckout()
    status = order.confirmPayment()
    generated_pin = order.generatePickupPin()

    # Assert
    assert status == "paid"
    assert order.is_paid is True
    assert generated_pin.isdigit() is True
    assert len(generated_pin) == 4
    assert order.pickup_pin == generated_pin


def test_order_complete_order_accepts_valid_pin(order: Order) -> None:
    # Arrange
    order.startCheckout()
    order.confirmPayment()
    generated_pin = order.generatePickupPin()

    # Act
    completed = order.completeOrder(generated_pin)

    # Assert
    assert completed is True
    assert order.status == "completed"


def test_order_complete_order_rejects_invalid_pin(order: Order) -> None:
    # Arrange
    order.startCheckout()
    order.confirmPayment()
    order.generatePickupPin()

    # Act / Assert
    with pytest.raises(InvalidPinError):
        order.completeOrder("9999")


def test_order_cannot_generate_pin_when_not_paid(order: Order) -> None:
    # Arrange
    assert order.is_paid is False

    # Act / Assert
    with pytest.raises(OrderNotPaidError):
        order.generatePickupPin()


def test_order_cannot_be_paid_twice(order: Order) -> None:
    # Arrange
    order.startCheckout()
    order.confirmPayment()

    # Act / Assert
    with pytest.raises(OrderAlreadyPaidError):
        order.confirmPayment()


def test_canteen_fulfillment_requires_exact_forward_transitions(order: Order) -> None:
    order.startCheckout()
    order.confirmPayment()

    with pytest.raises(InvalidOrderStatusTransitionError):
        order.advance_canteen_fulfillment(Order.STATUS_READY_FOR_PICKUP)

    assert order.advance_canteen_fulfillment(Order.STATUS_PREPARING) == Order.STATUS_PREPARING
    assert order.advance_canteen_fulfillment(Order.STATUS_READY_FOR_PICKUP) == Order.STATUS_READY_FOR_PICKUP

    with pytest.raises(InvalidOrderStatusTransitionError):
        order.advance_canteen_fulfillment(Order.STATUS_PREPARING)

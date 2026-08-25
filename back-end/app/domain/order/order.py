"""Order context: order aggregate root."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.exceptions import (
    EmptyOrderError,
    InvalidOrderStatusTransitionError,
    InvalidPinError,
    OrderAlreadyCompletedError,
    OrderAlreadyPaidError,
    OrderNotPaidError,
    OrderNotReadyForCheckoutError,
)
from app.domain.order.order_item import OrderItem


@dataclass
class Order:
    """Aggregate root representing the order placed by a user."""

    STATUS_DRAFT = "draft"
    STATUS_AWAITING_PAYMENT = "Awaiting Payment"
    STATUS_PAID = "paid"
    STATUS_PREPARING = "preparing"
    STATUS_IN_TRANSIT = "in_transit"
    STATUS_READY_FOR_PICKUP = "ready_for_pickup"
    STATUS_COMPLETED = "completed"

    id: str
    user_id: str
    items: list[OrderItem] = field(default_factory=list)
    status: str = STATUS_DRAFT
    is_paid: bool = False
    pickup_pin: str | None = None
    canteen_id: str | None = None
    drop_off_zone_id: str | None = None
    fulfillment_type: str = "delivery"
    delivery_ride_id: str | None = None
    delivery_fee: Decimal = Decimal("0.00")
    canteen_commission: Decimal = Decimal("0.00")
    courier_reward: Decimal = Decimal("0.00")

    def start_checkout(self) -> str:
        """Begin the checkout process for the order."""
        if self.is_paid:
            raise OrderAlreadyPaidError("This order has already been paid and cannot be checked out again.")
        if not self.items:
            raise OrderNotReadyForCheckoutError("An order without items cannot start checkout.")
        if self.status != self.STATUS_DRAFT:
            raise InvalidOrderStatusTransitionError(
                f"Cannot start checkout when order is in status '{self.status}'."
            )

        self.status = self.STATUS_AWAITING_PAYMENT
        return self.status

    def mark_as_paid(self) -> str:
        """Confirm the order payment."""
        if self.is_paid:
            raise OrderAlreadyPaidError("This order is already paid.")
        if self.status not in {self.STATUS_DRAFT, self.STATUS_AWAITING_PAYMENT}:
            raise InvalidOrderStatusTransitionError(
                f"Cannot mark order as paid from status '{self.status}'."
            )

        self.is_paid = True
        self.status = self.STATUS_PAID
        return self.status

    def attach_delivery_ride(self, delivery_ride_id: str) -> str:
        """Associate the order with a delivery ride before dispatch."""
        if not delivery_ride_id:
            raise ValueError("A valid delivery ride identifier is required.")
        self.delivery_ride_id = delivery_ride_id
        return self.delivery_ride_id

    def mark_as_in_transit(self) -> str:
        """Move the order to the in-transit stage."""
        if not self.is_paid:
            raise OrderNotPaidError("Order must be paid before it can be dispatched.")
        if self.delivery_ride_id is None:
            raise InvalidOrderStatusTransitionError(
                "Order must be linked to a delivery ride before it can be marked as in transit."
            )
        if self.status != self.STATUS_PAID:
            raise InvalidOrderStatusTransitionError(
                f"Cannot mark order as in transit from status '{self.status}'."
            )

        self.status = self.STATUS_IN_TRANSIT
        return self.status

    def advance_canteen_fulfillment(self, target_status: str) -> str:
        """Advance the canteen-owned fulfillment flow by exactly one state."""
        allowed_transition = {
            self.STATUS_PAID: self.STATUS_PREPARING,
            self.STATUS_PREPARING: self.STATUS_READY_FOR_PICKUP,
        }
        expected = allowed_transition.get(self.status)
        if expected is None or target_status != expected:
            raise InvalidOrderStatusTransitionError(
                f"Cannot move order from '{self.status}' to '{target_status}'."
            )
        self.status = target_status
        return self.status

    def mark_as_ready_for_pickup(self) -> str:
        """Mark the order as ready for student pickup."""
        if not self.is_paid:
            raise OrderNotPaidError("Order must be paid before it can be made available for pickup.")
        if self.status not in {self.STATUS_PAID, self.STATUS_IN_TRANSIT}:
            raise InvalidOrderStatusTransitionError(
                f"Cannot mark order as ready for pickup from status '{self.status}'."
            )

        self.status = self.STATUS_READY_FOR_PICKUP
        return self.status

    def generate_pickup_pin(self) -> str:
        """Generate a fresh 4-digit pickup pin for the customer."""
        if not self.is_paid:
            raise OrderNotPaidError("Order must be paid before a pickup pin can be generated.")
        if self.status not in {self.STATUS_PAID, self.STATUS_IN_TRANSIT, self.STATUS_READY_FOR_PICKUP}:
            raise InvalidOrderStatusTransitionError(
                f"Cannot generate pickup pin from status '{self.status}'."
            )

        self.pickup_pin = f"{random.randint(1000, 9999):04d}"
        self.status = self.STATUS_READY_FOR_PICKUP
        return self.pickup_pin

    def complete_order(self, provided_pin: str | None = None) -> bool:
        """Complete the order only when the generated pickup pin matches."""
        if not self.is_paid:
            raise OrderNotPaidError("Order must be paid before it can be completed.")
        if self.status == self.STATUS_COMPLETED:
            raise OrderAlreadyCompletedError("This order has already been completed.")
        if self.status != self.STATUS_READY_FOR_PICKUP:
            raise InvalidOrderStatusTransitionError(
                f"Cannot complete order from status '{self.status}'."
            )
        if self.pickup_pin is None:
            raise InvalidPinError("A pickup pin must be generated before the order is completed.")

        resolved_pin = self.pickup_pin if provided_pin is None else provided_pin
        if resolved_pin is None or resolved_pin.strip() != self.pickup_pin:
            raise InvalidPinError("The pickup pin does not match the generated one.")

        self.status = self.STATUS_COMPLETED
        return True

    def set_financial_breakdown(
        self,
        delivery_fee: Decimal,
        canteen_commission: Decimal,
        courier_reward: Decimal,
    ) -> None:
        """Store the financial breakdown calculated during checkout."""
        self.delivery_fee = delivery_fee
        self.canteen_commission = canteen_commission
        self.courier_reward = courier_reward

    def subtotal(self) -> Decimal:
        """Return the subtotal without delivery fee."""
        if not self.items:
            raise EmptyOrderError("The order must contain at least one item.")
        return sum((item.calculateSubtotal() for item in self.items), Decimal("0.00"))

    def total(self) -> Decimal:
        """Return the subtotal for backward compatibility with existing code."""
        return self.subtotal()

    def total_with_delivery(self) -> Decimal:
        """Return the amount charged to the student wallet."""
        return self.subtotal() + self.delivery_fee

    def startCheckout(self) -> str:
        return self.start_checkout()

    def confirmPayment(self) -> str:
        return self.mark_as_paid()

    def generatePickupPin(self) -> str:
        return self.generate_pickup_pin()

    def completeOrder(self, provided_pin: str | None = None) -> bool:
        return self.complete_order(provided_pin)

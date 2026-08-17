"""Use case for confirming pickup and completing a delivery."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.application.ports.repositories import IOrderRepository, IWalletRepository
from app.domain.financial.wallet import Wallet
from app.domain.order.order import Order


@dataclass
class ConfirmPickupAndCompleteUseCase:
    """Validate the pickup pin, complete the order, and credit the courier's wallet."""

    order_repository: IOrderRepository
    wallet_repository: IWalletRepository
    delivery_fee: Decimal = Decimal("5.00")

    def execute(self, order_id: str, courier_id: str, provided_pin: str) -> Order:
        """Validate the pickup code and credit delivery compensation to the courier."""
        if not order_id:
            raise ValueError("A valid order identifier is required.")
        if not courier_id:
            raise ValueError("A valid courier identifier is required.")
        if provided_pin is None:
            raise ValueError("A pickup pin must be provided to confirm delivery.")

        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise ValueError("The order does not exist.")

        if not order.is_paid:
            order.confirmPayment()

        if order.pickup_pin is None:
            raise ValueError("The order does not have a pickup pin yet; it must be generated before completion.")

        if order.status != Order.STATUS_READY_FOR_PICKUP:
            order.mark_as_ready_for_pickup()

        order.completeOrder(provided_pin)

        wallet = self.wallet_repository.get_by_user_id(courier_id)
        if wallet is None:
            wallet = Wallet(id=f"wallet-{courier_id}", user_id=courier_id, balance=Decimal("0"))

        wallet.creditDeliveryFee(self.delivery_fee)
        self.wallet_repository.save(wallet)

        self.order_repository.save(order)
        return order

"""Transactional use case for checking out an order in the platform."""

from __future__ import annotations

from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.application.ports.repositories import (
    IDropOffZoneRepository,
    IOrderRepository,
    IProductRepository,
    IWalletRepository,
)
from app.domain.exceptions import WalletNotFoundError
from app.domain.financial.pricing_strategies import (
    CanteenCommissionStrategy,
    CourierRewardStrategy,
    DeliveryFeeStrategy,
    StandardCommissionStrategy,
    StandardCourierRewardStrategy,
    StandardFeeStrategy,
)
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


@dataclass
class CheckoutOrderUseCase:
    """Create a paid order by validating items, charging the wallet, and persisting the transaction."""

    session: Session
    order_repository: IOrderRepository
    drop_off_zone_repository: IDropOffZoneRepository
    product_repository: IProductRepository
    wallet_repository: IWalletRepository
    delivery_fee_strategy: DeliveryFeeStrategy = field(default_factory=StandardFeeStrategy)
    canteen_commission_strategy: CanteenCommissionStrategy = field(default_factory=StandardCommissionStrategy)
    courier_reward_strategy: CourierRewardStrategy = field(default_factory=StandardCourierRewardStrategy)

    def execute(
        self,
        user_id: str,
        zone_id: str,
        items: list[OrderItem],
        order_id: str | None = None,
        canteen_id: str | None = None,
    ) -> Order:
        """Create and pay an order atomically using the student's wallet."""
        if not user_id:
            raise ValueError("A user identifier is required to start checkout.")
        if not items:
            raise ValueError("At least one item is required to checkout an order.")

        zone = self.drop_off_zone_repository.get_by_id(zone_id)
        if zone is None:
            raise ValueError("The selected drop-off zone does not exist.")

        wallet = self.wallet_repository.get_by_user_id(user_id)
        if wallet is None:
            raise WalletNotFoundError("The student's wallet does not exist.")

        resolved_order_id = order_id or f"order-{user_id}-{len(items)}"
        order = Order(
            id=resolved_order_id,
            user_id=user_id,
            items=list(items),
            status=Order.STATUS_DRAFT,
            is_paid=False,
            pickup_pin=None,
            canteen_id=canteen_id,
            drop_off_zone_id=zone_id,
        )

        subtotal = order.total()
        for item in items:
            product = self.product_repository.get_by_id(item.product_id)
            if product is None:
                raise ValueError(f"Product '{item.product_id}' does not exist.")
            if not product.is_active:
                raise ValueError(f"Product '{item.product_id}' is not active for sale.")

        delivery_fee = self.delivery_fee_strategy.calculate(subtotal)
        canteen_commission = self.canteen_commission_strategy.calculate(subtotal)
        courier_reward = self.courier_reward_strategy.calculate(subtotal, delivery_fee)
        order.set_financial_breakdown(delivery_fee, canteen_commission, courier_reward)

        try:
            zone.addLoad(1)
            order.start_checkout()
            wallet.debitOrderAmount(order.total_with_delivery())
            order.mark_as_paid()

            self.drop_off_zone_repository.save(zone)
            self.wallet_repository.save(wallet)
            persisted_order = self.order_repository.add(order)
            persisted_order.set_financial_breakdown(delivery_fee, canteen_commission, courier_reward)
            self.session.commit()
            return persisted_order
        except Exception:
            self.session.rollback()
            raise

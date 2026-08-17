"""Business services for order-related operations."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.application.ports.repositories import IOrderRepository, IProductRepository, IWalletRepository
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


@dataclass
class OrderService:
    order_repo: IOrderRepository
    product_repo: IProductRepository
    wallet_repo: IWalletRepository

    def create_order(self, order: Order) -> Order:
        if not order.items:
            raise ValueError("Order must contain at least one item")
        return self.order_repo.add(order)

    def add_item(self, order: Order, item: OrderItem) -> Order:
        # validate product
        product = self.product_repo.get_by_id(item.product_id)
        if product is None:
            raise ValueError("Product not found")
        # reserve stock in domain
        product.reserveStock(item.quantity)
        self.product_repo.save(product)
        order.items.append(item)
        return self.order_repo.save(order)

    def checkout(self, order: Order) -> Order:
        order.startCheckout()
        return self.order_repo.save(order)

    def confirm_payment(self, order: Order, amount: Decimal) -> Order:
        order.confirmPayment()
        # create payment transaction handled elsewhere; persist order state
        return self.order_repo.save(order)

    def generate_pickup_pin(self, order: Order) -> str:
        pin = order.generatePickupPin()
        self.order_repo.save(order)
        return pin

    def complete_order(self, order: Order, provided_pin: str | None = None) -> bool:
        res = order.completeOrder(provided_pin)
        self.order_repo.save(order)
        return res

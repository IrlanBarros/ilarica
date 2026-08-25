"""Transactional application service for secure order creation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.database.models import (
    CanteenModel,
    DropOffZoneModel,
    OrderItemModel,
    OrderModel,
    ProductModel,
)
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem
from app.repositories.sqlalchemy_repositories import SQLAlchemyOrderRepository


class OrderCreationError(ValueError):
    """Expected application error, translated to HTTP only by the router."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CreatedOrderItem:
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class CreatedOrder:
    id: UUID
    customer_id: UUID
    canteen_id: UUID
    drop_off_zone_id: UUID | None
    fulfillment_type: str
    status: str
    total_amount: Decimal
    items: tuple[CreatedOrderItem, ...]
    pickup_pin: str | None


class OrderCreationService:
    """Validate, price and persist an order in one database transaction."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        authenticated_customer_id: UUID,
        customer_id: str,
        canteen_id: str,
        fulfillment_type: str,
        drop_off_zone_id: str | None,
        items: list[tuple[str, int]],
    ) -> CreatedOrder:
        write_started = False
        try:
            customer_uuid = self._uuid(customer_id, "customer")
            canteen_uuid = self._uuid(canteen_id, "canteen")
            zone_uuid = self._uuid(drop_off_zone_id, "drop-off zone") if drop_off_zone_id else None
            if customer_uuid != authenticated_customer_id:
                raise OrderCreationError("forbidden", "The order customer must match the authenticated user")

            canteen = (
                self.session.query(CanteenModel)
                .filter(CanteenModel.id == canteen_uuid)
                .with_for_update()
                .one_or_none()
            )
            if canteen is None:
                raise OrderCreationError("not_found", "Canteen not found")
            if not canteen.is_open:
                raise OrderCreationError("conflict", "The selected canteen is currently unavailable")

            if fulfillment_type == "delivery":
                self._validate_delivery_zone(zone_uuid)

            product_ids = [self._uuid(product_id, "product") for product_id, _ in items]
            if len(product_ids) != len(set(product_ids)):
                raise OrderCreationError("invalid", "Duplicate products are not allowed")
            products = (
                self.session.query(ProductModel)
                .filter(ProductModel.id.in_(product_ids))
                .with_for_update()
                .all()
            )
            product_by_id = {product.id: product for product in products}
            domain_items: list[OrderItem] = []
            for (raw_product_id, quantity), product_id in zip(items, product_ids, strict=True):
                product = product_by_id.get(product_id)
                if product is None:
                    raise OrderCreationError("not_found", f"Product '{raw_product_id}' not found")
                if product.canteen_id != canteen_uuid:
                    raise OrderCreationError("invalid", "All products must belong to the selected canteen")
                if not product.is_active:
                    raise OrderCreationError("conflict", f"Product '{product.name}' is unavailable")
                domain_items.append(
                    OrderItem(
                        product_id=str(product.id),
                        product_name=product.name,
                        quantity=quantity,
                        unit_price=Decimal(str(product.price)),
                    )
                )

            order = Order(
                id=str(uuid4()),
                user_id=str(customer_uuid),
                canteen_id=str(canteen_uuid),
                drop_off_zone_id=str(zone_uuid) if zone_uuid else None,
                fulfillment_type=fulfillment_type,
                items=domain_items,
                status="draft",
                is_paid=False,
            )
            write_started = True
            SQLAlchemyOrderRepository(self.session).add(order)
            persisted = next(
                model
                for model in self.session.identity_map.values()
                if isinstance(model, OrderModel) and model.id == UUID(order.id)
            )
            result = CreatedOrder(
                id=persisted.id,
                customer_id=persisted.customer_id,
                canteen_id=persisted.canteen_id,
                drop_off_zone_id=persisted.drop_off_zone_id,
                fulfillment_type=persisted.fulfillment_type,
                status=persisted.status.value if hasattr(persisted.status, "value") else str(persisted.status),
                total_amount=Decimal(str(persisted.total_amount)),
                items=tuple(
                    CreatedOrderItem(
                        id=item.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        unit_price=Decimal(str(item.unit_price)),
                    )
                    for item in persisted.items
                ),
                pickup_pin=persisted.pickup_pin,
            )
            self.session.commit()
            return result
        except OrderCreationError:
            if write_started:
                self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise

    def _validate_delivery_zone(self, zone_id: UUID | None) -> None:
        if zone_id is None:
            raise OrderCreationError("invalid", "A drop-off zone is required for delivery")
        zone = (
            self.session.query(DropOffZoneModel)
            .filter(DropOffZoneModel.id == zone_id)
            .with_for_update()
            .one_or_none()
        )
        if zone is None:
            raise OrderCreationError("not_found", "Drop-off zone not found")
        if not zone.is_active:
            raise OrderCreationError("conflict", "The selected drop-off zone is unavailable")
        current_load = (
            self.session.query(OrderModel)
            .filter(OrderModel.drop_off_zone_id == zone.id, OrderModel.status != "completed")
            .count()
        )
        if current_load >= zone.capacity:
            raise OrderCreationError("conflict", "The selected drop-off zone is at capacity")

    @staticmethod
    def _uuid(value: str, field_name: str) -> UUID:
        try:
            return UUID(value)
        except (TypeError, ValueError) as exc:
            raise OrderCreationError("invalid_uuid", f"Invalid {field_name} UUID") from exc

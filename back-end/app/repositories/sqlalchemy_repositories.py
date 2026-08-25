"""SQLAlchemy-backed repository implementations for application ports.

These classes implement the interfaces declared in
`app.application.ports.repositories` using an injected SQLAlchemy
`Session`. Repositories are intentionally thin and focus only on
persistence and simple queries; business rules live in the service
layer.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, selectinload

from app.application.ports.repositories import (
    IDeliveryRideRepository,
    ICanteenRepository,
    IInvitationKeyRepository,
    IOrderRepository,
    IProductRepository,
    IWalletRepository,
    IUserRepository,
)
from app.database.models import (
    DeliveryRideModel,
    CanteenModel,
    InvitationKeyModel,
    OrderModel,
    OrderItemModel,
    OrderStatus,
    ProductModel,
    WalletModel,
    UserModel,
)
from app.domain.access_identity.invitation_key import InvitationKey
from app.domain.access_identity.user import User
from app.domain.catalog.product import Product
from app.domain.catalog.canteen import Canteen
from app.domain.financial.wallet import Wallet
from app.domain.logistics.delivery_ride import DeliveryRide
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


def _to_domain_user(model: UserModel) -> User:
    return User(
        id=model.id,
        name=model.name,
        email=model.email,
        whatsapp=model.whatsapp,
        password_hash=getattr(model, "password_hash", ""),
        role=getattr(model, "role_type", "customer"),
        is_active=model.is_active,
        is_email_validated=model.is_email_validated,
    )


def _to_domain_product(model: ProductModel) -> Product:
    return Product(
        id=str(model.id),
        name=model.name,
        price=Decimal(str(model.price)),
        is_active=model.is_active,
        stock_quantity=0,
        is_fast_stock_enabled=model.is_fast_stock_enabled,
        canteen_id=str(model.canteen_id),
        description=model.description,
        image_url=model.image_url,
    )


def _to_domain_canteen(model: CanteenModel) -> Canteen:
    return Canteen(
        id=str(model.id),
        user_id=str(model.user_id),
        name=model.name,
        location=model.location,
        is_open=model.is_open,
        products=[str(product.id) for product in model.products],
        opening_hours=model.opening_hours or [],
    )


def _to_domain_order(model: OrderModel) -> Order:
    return Order(
        id=str(model.id),
        user_id=str(model.customer_id),
        items=[
            OrderItem(
                product_id=str(item.product_id),
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
            )
            for item in model.items
        ],
        status=str(model.status),
        is_paid=str(model.status) in {Order.STATUS_PAID, Order.STATUS_IN_TRANSIT, Order.STATUS_READY_FOR_PICKUP, Order.STATUS_COMPLETED},
        pickup_pin=model.pickup_pin,
        canteen_id=str(model.canteen_id),
        drop_off_zone_id=str(model.drop_off_zone_id) if model.drop_off_zone_id else None,
        fulfillment_type=model.fulfillment_type,
        delivery_ride_id=str(model.delivery_ride.id) if getattr(model, "delivery_ride", None) else None,
    )


def _to_domain_wallet(model: WalletModel) -> Wallet:
    return Wallet(id=str(model.id), user_id=str(model.user_id), balance=Decimal(str(model.available_balance)))


class SQLAlchemyUserRepository(IUserRepository):
    """Concrete `IUserRepository` backed by SQLAlchemy models."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        model = self.session.get(UserModel, user_id)
        return _to_domain_user(model) if model is not None else None

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserModel).filter_by(email=email).one_or_none()
        return _to_domain_user(model) if model is not None else None

    def save(self, user: User) -> User:
        model = self.session.get(UserModel, user.id)
        if model is None:
            model = UserModel(
                id=user.id,
                name=user.name,
                email=user.email,
                whatsapp=user.whatsapp,
                password_hash=user.password_hash,
                role_type=user.role,
                is_active=user.is_active,
                is_email_validated=user.is_email_validated,
            )
            self.session.add(model)
        else:
            model.name = user.name
            model.email = user.email
            model.whatsapp = user.whatsapp
            model.password_hash = user.password_hash
            model.role_type = user.role
        self.session.flush()
        return _to_domain_user(model)

    def add(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            name=user.name,
            email=user.email,
            whatsapp=user.whatsapp,
            password_hash=user.password_hash,
            role_type=user.role,
            is_active=user.is_active,
            is_email_validated=user.is_email_validated,
        )
        self.session.add(model)
        self.session.flush()
        return _to_domain_user(model)


class SQLAlchemyInvitationKeyRepository(IInvitationKeyRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_value(self, key_value: str) -> Optional[InvitationKey]:
        model = self.session.query(InvitationKeyModel).filter_by(key_string=key_value).one_or_none()
        if model is None:
            return None
        return InvitationKey(
            key=model.key_string,
            issued_to_email="",
            expires_at=model.expires_at,
            used_by_user_id=model.id,
            is_used=model.is_used,
            is_expired=model.is_used,
        )

    def save(self, invitation_key: InvitationKey) -> InvitationKey:
        model = self.session.query(InvitationKeyModel).filter_by(key_string=invitation_key.key).one_or_none()
        if model is None:
            model = InvitationKeyModel(
                id=uuid4(),
                key_string=invitation_key.key,
                is_used=invitation_key.is_used,
                expires_at=invitation_key.expires_at,
            )
            self.session.add(model)
        else:
            model.is_used = invitation_key.is_used
            model.expires_at = invitation_key.expires_at
        self.session.flush()
        return invitation_key

    def consume(self, invitation_key: InvitationKey, user_id: UUID) -> InvitationKey:
        invitation_key.consume(user_id)
        return self.save(invitation_key)


class SQLAlchemyProductRepository(IProductRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, product_id: str) -> Optional[Product]:
        model = self.session.get(ProductModel, product_id)
        return _to_domain_product(model) if model is not None else None

    def save(self, product: Product) -> Product:
        model = self.session.get(ProductModel, product.id)
        canteen_id = product.canteen_id
        if model is None:
            model = ProductModel(
                id=product.id,
                canteen_id=canteen_id,
                name=product.name,
                price=float(product.price),
                is_active=product.is_active,
                is_fast_stock_enabled=product.is_fast_stock_enabled,
                description=product.description,
                image_url=product.image_url,
            )
            self.session.add(model)
        else:
            model.name = product.name
            model.price = float(product.price)
            model.is_active = product.is_active
            model.is_fast_stock_enabled = product.is_fast_stock_enabled
            model.description = product.description
            model.image_url = product.image_url
            if canteen_id is not None:
                model.canteen_id = canteen_id
        self.session.flush()
        return _to_domain_product(model)

    def list_by_ids(self, product_ids: Iterable[str]) -> List[Product]:
        models = self.session.query(ProductModel).filter(ProductModel.id.in_(list(product_ids))).all()
        return [_to_domain_product(m) for m in models]


class SQLAlchemyCanteenRepository(ICanteenRepository):
    """Concrete canteen repository backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, canteen: Canteen) -> Canteen:
        model = CanteenModel(
            id=UUID(canteen.id),
            user_id=UUID(canteen.user_id),
            name=canteen.name,
            location=canteen.location,
            is_open=canteen.is_open,
            opening_hours=canteen.opening_hours,
        )
        self.session.add(model)
        self.session.flush()
        return _to_domain_canteen(model)

    def save(self, canteen: Canteen) -> Canteen:
        model = self.session.get(CanteenModel, UUID(canteen.id))
        if model is None:
            raise ValueError("The canteen does not exist.")
        model.name = canteen.name
        model.location = canteen.location
        model.is_open = canteen.is_open
        model.opening_hours = canteen.opening_hours
        self.session.flush()
        return _to_domain_canteen(model)

    def get_by_id(self, canteen_id: str) -> Canteen | None:
        model = (
            self.session.query(CanteenModel)
            .options(selectinload(CanteenModel.products))
            .filter(CanteenModel.id == UUID(canteen_id))
            .one_or_none()
        )
        return _to_domain_canteen(model) if model is not None else None

    def list_all(self) -> list[Canteen]:
        models = (
            self.session.query(CanteenModel)
            .options(selectinload(CanteenModel.products))
            .order_by(CanteenModel.name.asc())
            .all()
        )
        return [_to_domain_canteen(model) for model in models]


class SQLAlchemyOrderRepository(IOrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, order_id: str) -> Optional[Order]:
        model = (
            self.session.query(OrderModel)
            .options(
                selectinload(OrderModel.items).selectinload(OrderItemModel.product),
                selectinload(OrderModel.delivery_ride),
            )
            .filter(OrderModel.id == UUID(order_id))
            .one_or_none()
        )
        return _to_domain_order(model) if model is not None else None

    def save(self, order: Order) -> Order:
        model = self.session.get(OrderModel, order.id)
        if model is None:
            model = OrderModel(
                id=UUID(order.id),
                customer_id=UUID(order.user_id),
                canteen_id=UUID(order.canteen_id),
                drop_off_zone_id=UUID(order.drop_off_zone_id) if order.drop_off_zone_id else None,
                fulfillment_type=order.fulfillment_type,
                status=OrderStatus(order.status),
                total_amount=float(order.total_with_delivery()),
                pickup_pin=order.pickup_pin,
            )
            self.session.add(model)
        else:
            model.status = OrderStatus(order.status) if isinstance(order.status, str) else order.status
            model.total_amount = float(order.total_with_delivery())
            model.pickup_pin = order.pickup_pin
        self.session.flush()
        return order

    def add(self, order: Order) -> Order:
        model = OrderModel(
            id=UUID(order.id),
            customer_id=UUID(order.user_id),
            canteen_id=UUID(order.canteen_id),
            drop_off_zone_id=UUID(order.drop_off_zone_id) if order.drop_off_zone_id else None,
            fulfillment_type=order.fulfillment_type,
            status=OrderStatus(order.status),
            total_amount=float(order.total_with_delivery()),
            pickup_pin=order.pickup_pin,
            items=[
                OrderItemModel(
                    id=uuid4(),
                    product_id=UUID(item.product_id),
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                )
                for item in order.items
            ],
        )
        self.session.add(model)
        self.session.flush()
        return order


class SQLAlchemyDeliveryRideRepository(IDeliveryRideRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, ride_id: str) -> Optional[DeliveryRide]:
        model = self.session.get(DeliveryRideModel, ride_id)
        if model is None:
            return None
        return DeliveryRide(
            id=str(model.id),
            order_id=str(model.order_id),
            status=model.status,
            assigned_courier_id=str(model.courier_id) if model.courier_id else None,
        )

    def get_by_order_id(self, order_id: str) -> Optional[DeliveryRide]:
        model = self.session.query(DeliveryRideModel).filter_by(order_id=order_id).one_or_none()
        if model is None:
            return None
        return DeliveryRide(
            id=str(model.id),
            order_id=str(model.order_id),
            status=model.status,
            assigned_courier_id=str(model.courier_id) if model.courier_id else None,
        )

    def save(self, ride: DeliveryRide) -> DeliveryRide:
        if ride.order_id is None:
            raise ValueError("A delivery ride must be linked to an order before it can be persisted.")
        model = self.session.get(DeliveryRideModel, ride.id)
        if model is None:
            model = DeliveryRideModel(
                id=ride.id,
                order_id=ride.order_id,
                courier_id=ride.assigned_courier_id,
                status=ride.status,
            )
            self.session.add(model)
        else:
            model.order_id = ride.order_id
            model.courier_id = UUID(ride.assigned_courier_id) if ride.assigned_courier_id else None
            model.status = ride.status
        self.session.flush()
        return ride


class SQLAlchemyWalletRepository(IWalletRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user_id(self, user_id: str) -> Optional[Wallet]:
        model = self.session.query(WalletModel).filter_by(user_id=user_id).one_or_none()
        return _to_domain_wallet(model) if model is not None else None

    def save(self, wallet: Wallet) -> Wallet:
        model = self.session.get(WalletModel, wallet.id)
        if model is None:
            model = WalletModel(id=wallet.id, user_id=wallet.user_id, available_balance=wallet.balance)
            self.session.add(model)
        else:
            model.available_balance = float(wallet.balance)
        self.session.flush()
        return _to_domain_wallet(model)

    def create_for_user(self, user_id: str) -> Wallet:
        model = WalletModel(user_id=user_id, available_balance=0)
        self.session.add(model)
        self.session.flush()
        return _to_domain_wallet(model)


__all__ = [
    "SQLAlchemyUserRepository",
    "SQLAlchemyInvitationKeyRepository",
    "SQLAlchemyProductRepository",
    "SQLAlchemyCanteenRepository",
    "SQLAlchemyOrderRepository",
    "SQLAlchemyDeliveryRideRepository",
    "SQLAlchemyWalletRepository",
]

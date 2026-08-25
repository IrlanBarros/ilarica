"""SQLAlchemy declarative models for the iLarica PostgreSQL schema."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OrderStatus(str, Enum):
    """Order lifecycle statuses."""

    DRAFT = "draft"
    AWAITING_PAYMENT = "Awaiting Payment"
    PAID = "paid"
    PREPARING = "preparing"
    IN_TRANSIT = "in_transit"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"


class UserModel(Base):
    """SQLAlchemy model for users in the identity and access context."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    whatsapp: Mapped[str] = mapped_column(String(15), nullable=False)
    # store a hashed password for authentication
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    role_type: Mapped[str] = mapped_column(String(50), nullable=False, default="customer")
    is_email_validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    canteens: Mapped[list["CanteenModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="customer",
        foreign_keys="OrderModel.customer_id",
        cascade="all, delete-orphan",
    )
    delivery_rides: Mapped[list["DeliveryRideModel"]] = relationship(
        back_populates="courier",
        foreign_keys="DeliveryRideModel.courier_id",
    )
    transport_kits: Mapped[list["TransportKitModel"]] = relationship(
        back_populates="courier",
        foreign_keys="TransportKitModel.courier_id",
    )
    wallets: Mapped[list["WalletModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reward_points: Mapped[list["RewardPointModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class InvitationKeyModel(Base):
    """SQLAlchemy model for invitation keys used by the closed ecosystem."""

    __tablename__ = "invitation_keys"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    key_string: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CanteenModel(Base):
    """SQLAlchemy model for campus canteens."""

    __tablename__ = "canteens"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped[UserModel] = relationship(back_populates="canteens")
    products: Mapped[list["ProductModel"]] = relationship(
        back_populates="canteen",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="canteen",
        foreign_keys="OrderModel.canteen_id",
        cascade="all, delete-orphan",
    )


class ProductModel(Base):
    """SQLAlchemy model for items sold by the canteen."""

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    canteen_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("canteens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_fast_stock_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    canteen: Mapped[CanteenModel] = relationship(back_populates="products")
    order_items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class DropOffZoneModel(Base):
    """SQLAlchemy model for physical delivery drop-off zones."""

    __tablename__ = "drop_off_zones"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="drop_off_zone",
        foreign_keys="OrderModel.drop_off_zone_id",
        cascade="all, delete-orphan",
    )


class OrderModel(Base):
    """SQLAlchemy model for customer orders."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    canteen_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("canteens.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    drop_off_zone_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drop_off_zones.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    status: Mapped[OrderStatus] = mapped_column(
        String(50),
        nullable=False,
        default=OrderStatus.AWAITING_PAYMENT,
    )
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    pickup_pin: Mapped[str | None] = mapped_column(String(4), nullable=True)

    customer: Mapped[UserModel] = relationship(
        back_populates="orders",
        foreign_keys=[customer_id],
    )
    canteen: Mapped[CanteenModel] = relationship(
        back_populates="orders",
        foreign_keys=[canteen_id],
    )
    drop_off_zone: Mapped[DropOffZoneModel] = relationship(
        back_populates="orders",
        foreign_keys=[drop_off_zone_id],
    )
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payment_transaction: Mapped["PaymentTransactionModel"] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )
    delivery_ride: Mapped["DeliveryRideModel"] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )


class OrderItemModel(Base):
    """SQLAlchemy model for products contained inside an order."""

    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    order_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped[OrderModel] = relationship(back_populates="items")
    product: Mapped[ProductModel] = relationship(back_populates="order_items")


class DeliveryRideModel(Base):
    """SQLAlchemy model for a ride assigned to a courier."""

    __tablename__ = "delivery_rides"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    order_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    courier_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    order: Mapped[OrderModel] = relationship(back_populates="delivery_ride")
    courier: Mapped[UserModel | None] = relationship(
        back_populates="delivery_rides",
        foreign_keys=[courier_id],
    )


class TransportKitModel(Base):
    """SQLAlchemy model for a courier transport kit."""

    __tablename__ = "transport_kits"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    courier_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    serial_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    is_allocated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    courier: Mapped[UserModel | None] = relationship(
        back_populates="transport_kits",
        foreign_keys=[courier_id],
    )


class PaymentTransactionModel(Base):
    """SQLAlchemy model for financial payment processing."""

    __tablename__ = "payment_transactions"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_payment_transactions_order_id"),
        UniqueConstraint("idempotency_key", name="uq_payment_transactions_idempotency_key"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    order_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default="internal")
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    pix_copy_paste: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped[OrderModel] = relationship(back_populates="payment_transaction")


class WalletModel(Base):
    """SQLAlchemy model for a user's wallet."""

    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    available_balance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    user: Mapped[UserModel] = relationship(back_populates="wallets")


class RewardPointModel(Base):
    """SQLAlchemy model for reward points accumulated by a user."""

    __tablename__ = "reward_points"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    points_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped[UserModel] = relationship(back_populates="reward_points")


__all__ = [
    "Base",
    "UserModel",
    "InvitationKeyModel",
    "CanteenModel",
    "ProductModel",
    "DropOffZoneModel",
    "OrderStatus",
    "OrderModel",
    "OrderItemModel",
    "DeliveryRideModel",
    "TransportKitModel",
    "PaymentTransactionModel",
    "WalletModel",
    "RewardPointModel",
]

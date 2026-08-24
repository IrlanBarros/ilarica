"""Pydantic DTOs for the iLarica application."""

from app.schemas.canteen_schemas import CanteenCreate, CanteenResponse, CanteenUpdate
from app.schemas.delivery_ride_schemas import DeliveryRideCreate, DeliveryRideResponse, DeliveryRideUpdate
from app.schemas.drop_off_zone_schemas import DropOffZoneCreate, DropOffZoneResponse, DropOffZoneUpdate
from app.schemas.invitation_key_schemas import InvitationKeyCreate, InvitationKeyResponse, InvitationKeyUpdate
from app.schemas.order_schemas import OrderCreate, OrderItemCreate, OrderItemResponse, OrderResponse, OrderUpdate
from app.schemas.payment_transaction_schemas import (
    PaymentIntentCreate,
    PaymentTransactionCreate,
    PaymentTransactionResponse,
    PaymentWebhookUpdate,
)
from app.schemas.product_schemas import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.transport_kit_schemas import TransportKitCreate, TransportKitResponse, TransportKitUpdate
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.schemas.wallet_schemas import WalletCreate, WalletResponse, WalletUpdate

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "CanteenCreate",
    "CanteenUpdate",
    "CanteenResponse",
    "InvitationKeyCreate",
    "InvitationKeyUpdate",
    "InvitationKeyResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "DropOffZoneCreate",
    "DropOffZoneUpdate",
    "DropOffZoneResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderItemCreate",
    "OrderItemResponse",
    "DeliveryRideCreate",
    "DeliveryRideUpdate",
    "DeliveryRideResponse",
    "PaymentTransactionCreate",
    "PaymentIntentCreate",
    "PaymentWebhookUpdate",
    "PaymentTransactionResponse",
    "TransportKitCreate",
    "TransportKitUpdate",
    "TransportKitResponse",
    "WalletCreate",
    "WalletUpdate",
    "WalletResponse",
]

"""Domain layer for the iLarica application."""

from app.domain.access_identity.institutional_email import InstitutionalEmail
from app.domain.access_identity.invitation_key import InvitationKey
from app.domain.access_identity.user import User
from app.domain.catalog.canteen import Canteen
from app.domain.catalog.product import Product
from app.domain.financial.payment_transaction import PaymentTransaction
from app.domain.financial.reward_point import RewardPoint
from app.domain.financial.wallet import Wallet
from app.domain.logistics.delivery_ride import DeliveryRide
from app.domain.logistics.drop_off_zone import DropOffZone
from app.domain.logistics.transport_kit import TransportKit
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem

__all__ = [
    "User",
    "InvitationKey",
    "Canteen",
    "Product",
    "Order",
    "OrderItem",
    "DropOffZone",
    "DeliveryRide",
    "TransportKit",
    "PaymentTransaction",
    "Wallet",
    "RewardPoint",
    "InstitutionalEmail",
]

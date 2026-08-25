"""Repository ports for the application layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Iterable
from uuid import UUID

from app.domain.access_identity.invitation_key import InvitationKey
from app.domain.access_identity.user import User
from app.domain.catalog.product import Product
from app.domain.catalog.canteen import Canteen
from app.domain.financial.wallet import Wallet
from app.domain.logistics.delivery_ride import DeliveryRide
from app.domain.logistics.drop_off_zone import DropOffZone
from app.domain.order.order import Order


class IUserRepository(ABC):
    """Persistence port for users."""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by its identifier."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Return a user by its email, if present."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Persist or update a user."""

    @abstractmethod
    def add(self, user: User) -> User:
        """Create a new user record."""


class IInvitationKeyRepository(ABC):
    """Persistence port for invitation keys."""

    @abstractmethod
    def get_by_value(self, key_value: str) -> InvitationKey | None:
        """Return a key by its value."""

    @abstractmethod
    def save(self, invitation_key: InvitationKey) -> InvitationKey:
        """Persist a key object."""

    @abstractmethod
    def consume(self, invitation_key: InvitationKey, user_id: UUID) -> InvitationKey:
        """Mark the invitation key as used by the given user."""


class IProductRepository(ABC):
    """Persistence port for products."""

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product | None:
        """Return a product by its identifier."""

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Persist or update a product."""

    @abstractmethod
    def list_by_ids(self, product_ids: Iterable[str]) -> list[Product]:
        """Return all products by the provided identifiers."""


class ICanteenRepository(ABC):
    """Persistence port for canteens."""

    @abstractmethod
    def add(self, canteen: Canteen) -> Canteen:
        """Create a canteen record."""

    @abstractmethod
    def save(self, canteen: Canteen) -> Canteen:
        """Persist changes to an existing canteen."""

    @abstractmethod
    def get_by_id(self, canteen_id: str) -> Canteen | None:
        """Return a canteen by its identifier."""

    @abstractmethod
    def list_all(self) -> list[Canteen]:
        """Return all canteens in display order."""


class IDropOffZoneRepository(ABC):
    """Persistence port for drop-off zones."""

    @abstractmethod
    def get_by_id(self, zone_id: str) -> DropOffZone | None:
        """Return a drop-off zone by its identifier."""

    @abstractmethod
    def save(self, zone: DropOffZone) -> DropOffZone:
        """Persist or update a drop-off zone."""


class IOrderRepository(ABC):
    """Persistence port for orders."""

    @abstractmethod
    def get_by_id(self, order_id: str) -> Order | None:
        """Return an order by its identifier."""

    @abstractmethod
    def save(self, order: Order) -> Order:
        """Persist or update an order."""

    @abstractmethod
    def add(self, order: Order) -> Order:
        """Create a new order record."""


class IDeliveryRideRepository(ABC):
    """Persistence port for delivery rides."""

    @abstractmethod
    def get_by_id(self, ride_id: str) -> DeliveryRide | None:
        """Return a delivery ride by its identifier."""

    @abstractmethod
    def get_by_order_id(self, order_id: str) -> DeliveryRide | None:
        """Return a delivery ride associated with an order when available."""

    @abstractmethod
    def save(self, ride: DeliveryRide) -> DeliveryRide:
        """Persist or update a delivery ride."""


class IWalletRepository(ABC):
    """Persistence port for wallets."""

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> Wallet | None:
        """Return the wallet for a given user."""

    @abstractmethod
    def save(self, wallet: Wallet) -> Wallet:
        """Persist or update a wallet."""

    @abstractmethod
    def create_for_user(self, user_id: str) -> Wallet:
        """Create an empty wallet for a user when one does not exist."""


class IPaymentGateway(ABC):
    """External payment gateway contract."""

    @abstractmethod
    def charge(self, order_id: str, amount: Decimal, currency: str = "BRL") -> str:
        """Call the external payment processor and return a transaction reference."""

    @abstractmethod
    def refund(self, order_id: str, amount: Decimal, currency: str = "BRL") -> bool:
        """Request a refund for an order."""


class INotificationService(ABC):
    """Optional notification port for downstream communication."""

    @abstractmethod
    def send_order_ready_notification(self, user_id: str, order_id: str) -> bool:
        """Notify the customer that their order is ready."""

    @abstractmethod
    def send_delivery_assignment_notification(self, courier_id: str, ride_id: str) -> bool:
        """Notify the courier that a ride was assigned."""

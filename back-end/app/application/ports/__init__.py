"""Application ports."""

from app.application.ports.repositories import (
    IDeliveryRideRepository,
    ICanteenRepository,
    IDropOffZoneRepository,
    IInvitationKeyRepository,
    INotificationService,
    IOrderRepository,
    IPaymentGateway,
    IProductRepository,
    IUserRepository,
    IWalletRepository,
)

__all__ = [
    "IUserRepository",
    "ICanteenRepository",
    "IInvitationKeyRepository",
    "IProductRepository",
    "IDropOffZoneRepository",
    "IOrderRepository",
    "IDeliveryRideRepository",
    "IWalletRepository",
    "IPaymentGateway",
    "INotificationService",
]

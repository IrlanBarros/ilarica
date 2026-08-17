"""Custom exceptions for the domain layer."""

from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain-level errors."""


class AuthenticationError(DomainError):
    """Raised when authentication fails."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when a password or credential does not match."""


class InvalidRoleError(DomainError):
    """Raised when a role is invalid for the current operation."""


class InvitationKeyError(DomainError):
    """Base exception for invitation key behavior."""


class InvitationKeyExpiredError(InvitationKeyError):
    """Raised when a key is expired."""


class InvitationKeyAlreadyUsedError(InvitationKeyError):
    """Raised when the key has already been consumed."""


class InvitationKeyNotUsableError(InvitationKeyError):
    """Raised when a key cannot be used yet."""


class CanteenOperationError(DomainError):
    """Base exception for canteen operations."""


class CanteenAlreadyOpenError(CanteenOperationError):
    """Raised when trying to open an already open canteen."""


class CanteenAlreadyClosedError(CanteenOperationError):
    """Raised when trying to close an already closed canteen."""


class ProductError(DomainError):
    """Base exception for product operations."""


class ProductAlreadyDisabledError(ProductError):
    """Raised when a product is already disabled."""


class ProductAlreadyEnabledError(ProductError):
    """Raised when a product is already enabled."""


class ProductOutOfStockError(ProductError):
    """Raised when stock is insufficient for a sale."""


class OrderError(DomainError):
    """Base exception for order operations."""


class OrderAlreadyPaidError(OrderError):
    """Raised when trying to pay an order that is already paid."""


class OrderNotPaidError(OrderError):
    """Raised when an action requires paid order status."""


class OrderAlreadyCompletedError(OrderError):
    """Raised when trying to complete an already completed order."""


class InvalidPinError(OrderError):
    """Raised when a pickup pin is invalid or does not match."""


class OrderNotReadyForCheckoutError(OrderError):
    """Raised when an order cannot start checkout in its current state."""


class InvalidOrderStatusTransitionError(OrderError):
    """Raised when an order status transition violates the state machine."""


class EmptyOrderError(OrderError):
    """Raised when an order operation requires at least one item."""


class DropOffZoneError(DomainError):
    """Base exception for drop-off zone operations."""


class DropOffZoneAlreadyActiveError(DropOffZoneError):
    """Raised when a zone is already active."""


class ZoneAtCapacityError(DropOffZoneError):
    """Raised when a zone has reached its capacity."""


class DeliveryRideError(DomainError):
    """Base exception for delivery ride logic."""


class DeliveryRideNotQueuedError(DeliveryRideError):
    """Raised when a delivery ride is not available to be accepted."""


class DeliveryRideAlreadyAcceptedError(DeliveryRideError):
    """Raised when a ride already has a courier assigned."""


class DeliveryRideNotAcceptedError(DeliveryRideError):
    """Raised when a delivery ride has not been accepted by a courier."""


class DeliveryRideAlreadyInTransitError(DeliveryRideError):
    """Raised when a delivery ride is already in transit."""


class DeliveryRideOrderMismatchError(DeliveryRideError):
    """Raised when a delivery ride cannot be matched with the expected order."""


class TransportKitError(DomainError):
    """Base exception for transport kit operations."""


class TransportKitAlreadyAllocatedError(TransportKitError):
    """Raised when trying to allocate a kit already assigned."""


class TransportKitNotAllocatedError(TransportKitError):
    """Raised when the kit must be assigned before returning."""


class PaymentTransactionError(DomainError):
    """Base exception for payment transaction behavior."""


class PaymentAlreadyProcessedError(PaymentTransactionError):
    """Raised when processing a payment more than once."""


class PaymentTransactionFailedError(PaymentTransactionError):
    """Raised when payment fails and a failure reason is required."""


class InvalidAmountError(PaymentTransactionError):
    """Raised when an amount is empty, zero, or negative."""


class WalletError(DomainError):
    """Base exception for wallet operations."""


class InvalidWithdrawalAmountError(WalletError):
    """Raised when a withdrawal amount is zero or negative."""


class WalletInsufficientFundsError(WalletError):
    """Raised when the wallet balance is insufficient."""


class WalletNotFoundError(WalletError):
    """Raised when a wallet is required for a financial operation but does not exist."""


class RewardPointError(DomainError):
    """Base exception for reward point operations."""


class InvalidRewardAmountError(RewardPointError):
    """Raised when a reward amount is invalid."""


class InsufficientRewardPointsError(RewardPointError):
    """Raised when there are not enough points to convert."""


class InvalidInstitutionalEmailError(DomainError):
    """Raised when a university email does not match an approved institutional domain."""

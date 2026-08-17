"""Financial and remuneration context: wallet aggregate root."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.exceptions import InvalidAmountError, InvalidWithdrawalAmountError, WalletInsufficientFundsError


@dataclass
class Wallet:
    """Aggregate root representing the user's financial wallet."""

    id: str
    user_id: str
    balance: Decimal = Decimal("0")
    pending_withdrawal: Decimal = Decimal("0")

    def can_afford(self, amount: Decimal) -> bool:
        """Return whether the wallet has enough available balance."""
        if amount <= Decimal("0"):
            raise InvalidAmountError("The amount evaluated against the wallet must be greater than zero.")
        return self.balance >= amount

    def credit(self, amount: Decimal) -> Decimal:
        """Credit the wallet with a positive amount."""
        if amount <= Decimal("0"):
            raise InvalidAmountError("The credited amount must be greater than zero.")

        self.balance += amount
        return self.balance

    def debit(self, amount: Decimal) -> Decimal:
        """Debit the wallet when a student pays for an order."""
        if amount <= Decimal("0"):
            raise InvalidAmountError("The debited amount must be greater than zero.")
        if amount > self.balance:
            raise WalletInsufficientFundsError("The wallet does not have enough balance for this operation.")

        self.balance -= amount
        return self.balance

    def creditDeliveryFee(self, amount: Decimal) -> Decimal:
        """Credit the wallet with an amount earned from deliveries."""
        return self.credit(amount)

    def debitOrderAmount(self, amount: Decimal) -> Decimal:
        """Backward-compatible alias for order checkout debits."""
        return self.debit(amount)

    def requestWithdrawal(self, amount: Decimal) -> Decimal:
        """Request a withdrawal from the wallet."""
        if amount <= Decimal("0"):
            raise InvalidWithdrawalAmountError("Withdrawal amount must be greater than zero.")
        if amount > self.balance:
            raise WalletInsufficientFundsError("The wallet does not have enough balance for this withdrawal.")

        self.balance -= amount
        self.pending_withdrawal += amount
        return self.pending_withdrawal

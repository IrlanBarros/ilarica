from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.exceptions import InvalidAmountError, InvalidWithdrawalAmountError, WalletInsufficientFundsError
from app.domain.financial.wallet import Wallet


@pytest.fixture
def wallet() -> Wallet:
    return Wallet(id="wallet-1", user_id="user-1", balance=Decimal("25.00"))


def test_wallet_credit_delivery_fee_increases_balance(wallet: Wallet) -> None:
    # Arrange
    amount = Decimal("10.00")

    # Act
    new_balance = wallet.creditDeliveryFee(amount)

    # Assert
    assert new_balance == Decimal("35.00")
    assert wallet.balance == Decimal("35.00")


def test_wallet_allows_withdrawal_when_balance_is_sufficient(wallet: Wallet) -> None:
    # Arrange
    amount = Decimal("15.00")

    # Act
    pending_withdrawal = wallet.requestWithdrawal(amount)

    # Assert
    assert pending_withdrawal == Decimal("15.00")
    assert wallet.balance == Decimal("10.00")
    assert wallet.pending_withdrawal == Decimal("15.00")


def test_wallet_rejects_withdrawal_when_balance_is_insufficient(wallet: Wallet) -> None:
    # Arrange
    amount = Decimal("100.00")

    # Act / Assert
    with pytest.raises(WalletInsufficientFundsError):
        wallet.requestWithdrawal(amount)


def test_wallet_rejects_invalid_withdrawal_amount(wallet: Wallet) -> None:
    # Arrange
    invalid_amounts = [Decimal("0.00"), Decimal("-1.00")]

    # Act / Assert
    for amount in invalid_amounts:
        with pytest.raises(InvalidWithdrawalAmountError):
            wallet.requestWithdrawal(amount)


def test_wallet_rejects_invalid_credit_amount() -> None:
    # Arrange
    wallet = Wallet(id="wallet-2", user_id="user-2", balance=Decimal("10.00"))

    # Act / Assert
    with pytest.raises(InvalidAmountError):
        wallet.creditDeliveryFee(Decimal("0.00"))

"""Business services for wallet-related operations."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.application.ports.repositories import IWalletRepository
from app.domain.financial.wallet import Wallet


@dataclass
class WalletService:
    wallet_repo: IWalletRepository

    def get_or_create_for_user(self, user_id: str) -> Wallet:
        wallet = self.wallet_repo.get_by_user_id(user_id)
        if wallet is None:
            return self.wallet_repo.create_for_user(user_id)
        return wallet

    def credit_delivery_fee(self, user_id: str, amount: Decimal) -> Wallet:
        wallet = self.get_or_create_for_user(user_id)
        wallet.creditDeliveryFee(amount)
        return self.wallet_repo.save(wallet)

    def request_withdrawal(self, user_id: str, amount: Decimal) -> Decimal:
        wallet = self.get_or_create_for_user(user_id)
        pending = wallet.requestWithdrawal(amount)
        self.wallet_repo.save(wallet)
        return pending

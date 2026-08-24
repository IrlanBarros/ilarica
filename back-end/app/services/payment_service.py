"""Transactional payment orchestration for Pix and the internal wallet."""

from __future__ import annotations

import base64
import hmac
import io
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import qrcode
import qrcode.image.svg
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import OrderModel, OrderStatus, PaymentTransactionModel, WalletModel


class PaymentFlowError(Exception):
    """Expected payment failure mapped to an HTTP response."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def is_expired(transaction: PaymentTransactionModel, now: datetime | None = None) -> bool:
    if transaction.expires_at is None:
        return False
    expires_at = transaction.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= (now or utc_now())


def build_pix_qr_data_url(payload: str) -> str:
    """Encode the server-created Pix payload into an SVG QR data URL."""
    stream = io.BytesIO()
    image = qrcode.make(payload, image_factory=qrcode.image.svg.SvgPathImage)
    image.save(stream)
    encoded = base64.b64encode(stream.getvalue()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


@dataclass
class PaymentService:
    db: Session

    def _owned_order(self, order_id: str, user_id: str) -> OrderModel:
        try:
            resolved_order_id = UUID(order_id)
        except ValueError as exc:
            raise PaymentFlowError(422, "Invalid order identifier") from exc

        order = (
            self.db.query(OrderModel)
            .filter(OrderModel.id == resolved_order_id)
            .with_for_update()
            .one_or_none()
        )
        if order is None:
            raise PaymentFlowError(404, "Order not found")
        if str(order.customer_id) != user_id:
            raise PaymentFlowError(403, "The authenticated user does not own this order")
        return order

    def create_intent(
        self,
        *,
        order_id: str,
        payment_method: str,
        idempotency_key: str,
        user_id: str,
    ) -> PaymentTransactionModel:
        normalized_key = idempotency_key.strip()
        if len(normalized_key) < 16 or len(normalized_key) > 128:
            raise PaymentFlowError(422, "Idempotency-Key must contain between 16 and 128 characters")

        existing_by_key = (
            self.db.query(PaymentTransactionModel)
            .filter(PaymentTransactionModel.idempotency_key == normalized_key)
            .one_or_none()
        )
        if existing_by_key is not None:
            order = self._owned_order(str(existing_by_key.order_id), user_id)
            if str(order.id) != order_id or existing_by_key.method != payment_method:
                raise PaymentFlowError(409, "Idempotency-Key was already used for another payment intent")
            return self.refresh_expiration(existing_by_key)

        order = self._owned_order(order_id, user_id)
        existing_for_order = (
            self.db.query(PaymentTransactionModel)
            .filter(PaymentTransactionModel.order_id == order.id)
            .with_for_update()
            .one_or_none()
        )
        if existing_for_order is not None:
            return self.refresh_expiration(existing_for_order)
        if order.status == OrderStatus.PAID.value:
            raise PaymentFlowError(409, "Order is already paid")
        if order.status not in {OrderStatus.DRAFT.value, OrderStatus.AWAITING_PAYMENT.value}:
            raise PaymentFlowError(409, "Order is not available for payment")

        amount = Decimal(str(order.total_amount)).quantize(Decimal("0.01"))
        if amount <= 0:
            raise PaymentFlowError(422, "Order total must be greater than zero")

        transaction = PaymentTransactionModel(
            id=uuid4(),
            order_id=order.id,
            amount=amount,
            method=payment_method,
            status="pending",
            idempotency_key=normalized_key,
            external_reference=f"ilarica-{uuid4().hex}",
        )

        if payment_method == "pix":
            expiration_minutes = int(os.getenv("PIX_EXPIRATION_MINUTES", "15"))
            transaction.expires_at = utc_now() + timedelta(minutes=expiration_minutes)
            transaction.pix_copy_paste = (
                f"ILARICA-SANDBOX|order={order.id}|amount={amount:.2f}|"
                f"reference={transaction.external_reference}"
            )
            order.status = OrderStatus.AWAITING_PAYMENT.value
        elif payment_method == "wallet":
            self._charge_wallet(transaction, order, user_id)
        else:
            raise PaymentFlowError(422, "Unsupported payment method")

        self.db.add(transaction)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            concurrent = (
                self.db.query(PaymentTransactionModel)
                .filter(PaymentTransactionModel.idempotency_key == normalized_key)
                .one_or_none()
            )
            if concurrent is not None:
                return concurrent
            raise PaymentFlowError(409, "A payment intent already exists for this order") from exc
        self.db.refresh(transaction)

        if transaction.status == "failed":
            raise PaymentFlowError(402, transaction.failure_reason or "Payment was declined")
        return transaction

    def _charge_wallet(
        self,
        transaction: PaymentTransactionModel,
        order: OrderModel,
        user_id: str,
    ) -> None:
        wallet = (
            self.db.query(WalletModel)
            .filter(WalletModel.user_id == UUID(user_id))
            .with_for_update()
            .one_or_none()
        )
        if wallet is None:
            transaction.status = "failed"
            transaction.failure_reason = "Digital wallet not found"
            return

        balance = Decimal(str(wallet.available_balance))
        amount = Decimal(str(transaction.amount))
        if balance < amount:
            transaction.status = "failed"
            transaction.failure_reason = "Insufficient wallet balance"
            return

        wallet.available_balance = balance - amount
        transaction.status = "succeeded"
        transaction.confirmed_at = utc_now()
        order.status = OrderStatus.PAID.value

    def get_owned(self, transaction_id: str, user_id: str) -> PaymentTransactionModel:
        try:
            resolved_id = UUID(transaction_id)
        except ValueError as exc:
            raise PaymentFlowError(422, "Invalid payment transaction identifier") from exc
        transaction = self.db.get(PaymentTransactionModel, resolved_id)
        if transaction is None:
            raise PaymentFlowError(404, "Payment transaction not found")
        self._owned_order(str(transaction.order_id), user_id)
        return self.refresh_expiration(transaction)

    def refresh_expiration(self, transaction: PaymentTransactionModel) -> PaymentTransactionModel:
        if transaction.status == "pending" and is_expired(transaction):
            transaction.status = "expired"
            transaction.failure_reason = "Pix payment expired"
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
        return transaction

    def confirm_provider_result(
        self,
        transaction_id: str,
        *,
        result: str,
        external_reference: str | None,
        failure_reason: str | None,
        provided_secret: str,
    ) -> PaymentTransactionModel:
        expected_secret = os.getenv("PAYMENT_WEBHOOK_SECRET", "")
        if not expected_secret or not hmac.compare_digest(provided_secret, expected_secret):
            raise PaymentFlowError(401, "Invalid payment webhook credentials")
        try:
            resolved_id = UUID(transaction_id)
        except ValueError as exc:
            raise PaymentFlowError(422, "Invalid payment transaction identifier") from exc

        transaction = (
            self.db.query(PaymentTransactionModel)
            .filter(PaymentTransactionModel.id == resolved_id)
            .with_for_update()
            .one_or_none()
        )
        if transaction is None:
            raise PaymentFlowError(404, "Payment transaction not found")
        if transaction.method != "pix":
            raise PaymentFlowError(409, "Only Pix intents may be confirmed by the provider")
        if transaction.status == "succeeded":
            return transaction
        if is_expired(transaction):
            transaction.status = "expired"
            transaction.failure_reason = "Pix payment expired"
            self.db.commit()
            raise PaymentFlowError(410, "Pix payment expired")

        order = (
            self.db.query(OrderModel)
            .filter(OrderModel.id == transaction.order_id)
            .with_for_update()
            .one()
        )
        transaction.external_reference = external_reference or transaction.external_reference
        if result == "failed":
            transaction.status = "failed"
            transaction.failure_reason = failure_reason or "Payment was declined"
        else:
            transaction.status = "succeeded"
            transaction.failure_reason = None
            transaction.confirmed_at = utc_now()
            order.status = OrderStatus.PAID.value
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

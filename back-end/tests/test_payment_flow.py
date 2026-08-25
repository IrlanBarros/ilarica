from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.database.models import OrderModel, OrderStatus, PaymentTransactionModel, WalletModel
from app.application.ports.payment_provider import PaymentProvider, PixCharge, PixChargeStatus
from app.services.payment_service import PaymentFlowError, PaymentService, utc_now


class FakePixProvider(PaymentProvider):
    name = "fake"

    def __init__(self) -> None:
        self.created_amount: Decimal | None = None
        self.status = "pending"
        self.paid_amount: Decimal | None = None
        self.status_calls = 0

    def create_pix_charge(self, *, reference, amount, expiration_seconds, order_id):
        self.created_amount = amount
        return PixCharge(reference=reference, copy_paste="provider-pix-code", expires_at=utc_now() + timedelta(seconds=expiration_seconds))

    def get_pix_charge(self, reference):
        self.status_calls += 1
        return PixChargeStatus(reference=reference, status=self.status, paid_amount=self.paid_amount)


def _order_and_wallet(db: Session, *, total: str = "18.00", balance: str = "50.00") -> tuple[OrderModel, WalletModel, UUID]:
    customer_id = uuid4()
    order = OrderModel(
        id=uuid4(),
        customer_id=customer_id,
        canteen_id=uuid4(),
        drop_off_zone_id=uuid4(),
        status=OrderStatus.DRAFT.value,
        total_amount=Decimal(total),
    )
    wallet = WalletModel(id=uuid4(), user_id=customer_id, available_balance=Decimal(balance))
    db.add_all([order, wallet])
    db.commit()
    return order, wallet, customer_id


def test_wallet_payment_is_atomic_and_idempotent(db_session: Session) -> None:
    order, wallet, customer_id = _order_and_wallet(db_session)
    service = PaymentService(db_session)

    first = service.create_intent(
        order_id=str(order.id),
        payment_method="wallet",
        idempotency_key="wallet-payment-key-0001",
        user_id=str(customer_id),
    )
    replay = service.create_intent(
        order_id=str(order.id),
        payment_method="wallet",
        idempotency_key="wallet-payment-key-0001",
        user_id=str(customer_id),
    )

    db_session.refresh(wallet)
    db_session.refresh(order)
    assert first.id == replay.id
    assert first.status == "succeeded"
    assert Decimal(str(wallet.available_balance)) == Decimal("32.00")
    assert order.status == OrderStatus.PAID.value
    assert db_session.query(PaymentTransactionModel).filter_by(order_id=order.id).count() == 1


def test_wallet_payment_persists_decline_without_negative_balance(db_session: Session) -> None:
    order, wallet, customer_id = _order_and_wallet(db_session, balance="10.00")

    with pytest.raises(PaymentFlowError) as error:
        PaymentService(db_session).create_intent(
            order_id=str(order.id),
            payment_method="wallet",
            idempotency_key="wallet-payment-key-0002",
            user_id=str(customer_id),
        )

    db_session.refresh(wallet)
    assert error.value.status_code == 402
    assert Decimal(str(wallet.available_balance)) == Decimal("10.00")
    transaction = db_session.query(PaymentTransactionModel).filter_by(order_id=order.id).one()
    assert transaction.status == "failed"
    assert transaction.failure_reason == "Insufficient wallet balance"


def test_pix_intent_expires_and_cannot_be_confirmed(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    order, _, customer_id = _order_and_wallet(db_session)
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET", "test-webhook-secret")
    transaction = PaymentService(db_session).create_intent(
        order_id=str(order.id),
        payment_method="pix",
        idempotency_key="pix-payment-key-0000001",
        user_id=str(customer_id),
    )
    assert transaction.pix_copy_paste
    assert transaction.expires_at

    transaction.expires_at = utc_now() - timedelta(seconds=1)
    db_session.commit()
    expired = PaymentService(db_session).get_owned(str(transaction.id), str(customer_id))
    assert expired.status == "expired"

    with pytest.raises(PaymentFlowError) as error:
        PaymentService(db_session).confirm_provider_result(
            str(transaction.id),
            result="succeeded",
            external_reference="provider-1",
            failure_reason=None,
            provided_secret="test-webhook-secret",
        )
    assert error.value.status_code == 410


def test_pix_webhook_is_authenticated_and_idempotent(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    order, _, customer_id = _order_and_wallet(db_session)
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET", "test-webhook-secret")
    transaction = PaymentService(db_session).create_intent(
        order_id=str(order.id),
        payment_method="pix",
        idempotency_key="pix-payment-key-0000002",
        user_id=str(customer_id),
    )
    service = PaymentService(db_session)

    with pytest.raises(PaymentFlowError) as unauthorized:
        service.confirm_provider_result(
            str(transaction.id), result="succeeded", external_reference=None,
            failure_reason=None, provided_secret="wrong-secret",
        )
    assert unauthorized.value.status_code == 401

    first = service.confirm_provider_result(
        str(transaction.id), result="succeeded", external_reference="provider-2",
        failure_reason=None, provided_secret="test-webhook-secret",
    )
    replay = service.confirm_provider_result(
        str(transaction.id), result="succeeded", external_reference="provider-2",
        failure_reason=None, provided_secret="test-webhook-secret",
    )
    db_session.refresh(order)
    assert first.id == replay.id
    assert replay.status == "succeeded"
    assert order.status == OrderStatus.PAID.value


def test_external_provider_uses_server_amount_and_reconciles_once(db_session: Session) -> None:
    order, _, customer_id = _order_and_wallet(db_session, total="18.00")
    provider = FakePixProvider()
    service = PaymentService(db_session, provider=provider)
    transaction = service.create_intent(
        order_id=str(order.id), payment_method="pix",
        idempotency_key="external-provider-key-0001", user_id=str(customer_id),
    )
    assert provider.created_amount == Decimal("18.00")
    assert transaction.pix_copy_paste == "provider-pix-code"
    assert transaction.provider == "fake"

    provider.status = "succeeded"
    provider.paid_amount = Decimal("18.00")
    confirmed = service.get_owned(str(transaction.id), str(customer_id))
    replay = service.get_owned(str(transaction.id), str(customer_id))
    db_session.refresh(order)
    assert confirmed.status == replay.status == "succeeded"
    assert order.status == OrderStatus.PAID.value
    assert provider.status_calls == 1


def test_external_provider_amount_mismatch_never_marks_order_paid(db_session: Session) -> None:
    order, _, customer_id = _order_and_wallet(db_session, total="18.00")
    provider = FakePixProvider()
    service = PaymentService(db_session, provider=provider)
    transaction = service.create_intent(
        order_id=str(order.id), payment_method="pix",
        idempotency_key="external-provider-key-0002", user_id=str(customer_id),
    )
    provider.status = "succeeded"
    provider.paid_amount = Decimal("0.01")
    result = service.reconcile_by_reference(str(transaction.external_reference))
    db_session.refresh(order)
    assert result is not None and result.status == "failed"
    assert result.failure_reason == "Provider payment amount mismatch"
    assert order.status != OrderStatus.PAID.value

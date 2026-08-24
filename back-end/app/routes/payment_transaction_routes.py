"""Authenticated and idempotent payment intent endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import OrderModel, PaymentTransactionModel, UserModel
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.payment_transaction_schemas import (
    PaymentIntentCreate,
    PaymentTransactionResponse,
    PaymentWebhookUpdate,
)
from app.services.payment_service import PaymentFlowError, PaymentService, build_pix_qr_data_url

router = APIRouter(prefix="/payment-transactions", tags=["Payment Transactions"])


def _response(transaction: PaymentTransactionModel) -> PaymentTransactionResponse:
    return PaymentTransactionResponse(
        id=str(transaction.id),
        order_id=str(transaction.order_id),
        amount=transaction.amount,
        payment_method=transaction.method,
        status=transaction.status,
        external_reference=transaction.external_reference,
        pix_copy_paste=transaction.pix_copy_paste,
        pix_qr_code=(
            build_pix_qr_data_url(transaction.pix_copy_paste)
            if transaction.pix_copy_paste and transaction.status == "pending"
            else None
        ),
        expires_at=transaction.expires_at,
        failure_reason=transaction.failure_reason,
        created_at=transaction.created_at,
        confirmed_at=transaction.confirmed_at,
    )


def _raise_payment_error(exc: PaymentFlowError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post(
    "/",
    response_model=PaymentTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Payment intent created or safely replayed."},
        401: {"description": "Authentication required."},
        402: {"description": "Wallet balance is insufficient or payment was declined."},
        409: {"description": "Order is already paid or intent conflicts."},
        422: {"description": "Invalid intent or idempotency key."},
    },
)
def create_payment_transaction(
    payload: PaymentIntentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> PaymentTransactionResponse:
    """Create a server-priced Pix or wallet intent exactly once."""
    try:
        transaction = PaymentService(db).create_intent(
            order_id=payload.order_id,
            payment_method=payload.payment_method,
            idempotency_key=idempotency_key,
            user_id=str(current_user.id),
        )
    except PaymentFlowError as exc:
        _raise_payment_error(exc)
    return _response(transaction)


@router.get("/", response_model=list[PaymentTransactionResponse])
def list_payment_transactions(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> list[PaymentTransactionResponse]:
    """List only payment transactions owned by the authenticated customer."""
    entries = (
        db.query(PaymentTransactionModel)
        .join(OrderModel, OrderModel.id == PaymentTransactionModel.order_id)
        .filter(OrderModel.customer_id == current_user.id)
        .order_by(PaymentTransactionModel.created_at.desc())
        .all()
    )
    service = PaymentService(db)
    return [_response(service.refresh_expiration(entry)) for entry in entries]


@router.post(
    "/webhooks/{transaction_id}",
    response_model=PaymentTransactionResponse,
    include_in_schema=False,
)
def confirm_payment_webhook(
    transaction_id: str,
    payload: PaymentWebhookUpdate,
    webhook_secret: str = Header(..., alias="X-Payment-Webhook-Secret"),
    db: Session = Depends(get_db),
) -> PaymentTransactionResponse:
    """Receive an idempotent Pix provider result; never callable with customer JWT alone."""
    try:
        transaction = PaymentService(db).confirm_provider_result(
            transaction_id,
            result=payload.status,
            external_reference=payload.external_reference,
            failure_reason=payload.failure_reason,
            provided_secret=webhook_secret,
        )
    except PaymentFlowError as exc:
        _raise_payment_error(exc)
    return _response(transaction)


@router.get("/{transaction_id}", response_model=PaymentTransactionResponse)
def get_payment_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> PaymentTransactionResponse:
    """Return the latest state for polling, restricted to the transaction owner."""
    try:
        transaction = PaymentService(db).get_owned(transaction_id, str(current_user.id))
    except PaymentFlowError as exc:
        _raise_payment_error(exc)
    return _response(transaction)

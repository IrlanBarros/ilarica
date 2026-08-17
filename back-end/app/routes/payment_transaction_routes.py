"""Payment transaction REST endpoints."""

from __future__ import annotations

from uuid import uuid4
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import PaymentTransactionModel
from app.database.session import get_db
from app.schemas.payment_transaction_schemas import PaymentTransactionCreate, PaymentTransactionResponse, PaymentTransactionUpdate

router = APIRouter(prefix="/payment-transactions", tags=["Payment Transactions"])


@router.post(
    "/",
    response_model=PaymentTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment transaction",
    responses={201: {"description": "Payment transaction created successfully."}, 400: {"description": "Invalid transaction payload."}},
)
def create_payment_transaction(payload: PaymentTransactionCreate, db: Session = Depends(get_db)) -> PaymentTransactionResponse:
    """Create a payment transaction."""
    transaction = PaymentTransactionModel(
        id=uuid4(),
        order_id=payload.order_id,
        amount=float(payload.amount),
        method=payload.payment_method,
        status=payload.status,
        external_reference=payload.external_reference,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return PaymentTransactionResponse(
        id=str(transaction.id),
        order_id=str(transaction.order_id),
        amount=Decimal(str(transaction.amount)),
        payment_method=transaction.method,
        status=transaction.status,
        external_reference=transaction.external_reference,
    )


@router.get(
    "/",
    response_model=list[PaymentTransactionResponse],
    summary="List payment transactions",
)
def list_payment_transactions(db: Session = Depends(get_db)) -> list[PaymentTransactionResponse]:
    """List payment transactions."""
    entries = db.query(PaymentTransactionModel).all()
    return [
        PaymentTransactionResponse(
            id=str(item.id),
            order_id=str(item.order_id),
            amount=Decimal(str(item.amount)),
            payment_method=item.method,
            status=item.status,
            external_reference=item.external_reference,
        )
        for item in entries
    ]


@router.get(
    "/{transaction_id}",
    response_model=PaymentTransactionResponse,
    summary="Get payment transaction by ID",
    responses={404: {"description": "Payment transaction not found."}},
)
def get_payment_transaction(transaction_id: str, db: Session = Depends(get_db)) -> PaymentTransactionResponse:
    """Get one payment transaction by ID."""
    transaction = db.get(PaymentTransactionModel, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment transaction not found")
    return PaymentTransactionResponse(
        id=str(transaction.id),
        order_id=str(transaction.order_id),
        amount=Decimal(str(transaction.amount)),
        payment_method=transaction.method,
        status=transaction.status,
        external_reference=transaction.external_reference,
    )


@router.patch(
    "/{transaction_id}",
    response_model=PaymentTransactionResponse,
    summary="Update payment transaction",
    responses={404: {"description": "Payment transaction not found."}, 400: {"description": "Invalid update payload."}},
)
def update_payment_transaction(transaction_id: str, payload: PaymentTransactionUpdate, db: Session = Depends(get_db)) -> PaymentTransactionResponse:
    """Patch a payment transaction."""
    transaction = db.get(PaymentTransactionModel, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment transaction not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "amount":
            transaction.amount = float(value)
        elif key == "payment_method":
            transaction.method = value
        elif key == "status":
            transaction.status = value
        elif key == "external_reference":
            transaction.external_reference = value

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return PaymentTransactionResponse(
        id=str(transaction.id),
        order_id=str(transaction.order_id),
        amount=Decimal(str(transaction.amount)),
        payment_method=transaction.method,
        status=transaction.status,
        external_reference=transaction.external_reference,
    )


@router.delete(
    "/{transaction_id}",
    summary="Delete payment transaction",
    responses={404: {"description": "Payment transaction not found."}},
)
def delete_payment_transaction(transaction_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a payment transaction by ID."""
    transaction = db.get(PaymentTransactionModel, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment transaction not found")

    db.delete(transaction)
    db.commit()
    return {"detail": "Payment transaction deleted successfully"}

"""Wallet REST endpoints."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import WalletModel
from app.database.session import get_db
from app.repositories.sqlalchemy_repositories import SQLAlchemyWalletRepository
from app.schemas.wallet_schemas import WalletCreate, WalletResponse, WalletUpdate
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post(
    "/",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create wallet",
    responses={201: {"description": "Wallet created successfully."}, 400: {"description": "Invalid wallet payload."}},
)
def create_wallet(payload: WalletCreate, db: Session = Depends(get_db)) -> WalletResponse:
    """Create a wallet for a user."""
    service = WalletService(SQLAlchemyWalletRepository(db))
    wallet = service.get_or_create_for_user(payload.user_id)
    if wallet.balance != Decimal(str(payload.balance)):
        wallet.balance = Decimal(str(payload.balance))
    saved = service.wallet_repo.save(wallet)
    return WalletResponse(
        id=str(saved.id),
        user_id=str(saved.user_id),
        balance=Decimal(str(saved.balance)),
        pending_withdrawal=Decimal(str(saved.pending_withdrawal)),
    )


@router.get(
    "/",
    response_model=list[WalletResponse],
    summary="List wallets",
)
def list_wallets(db: Session = Depends(get_db)) -> list[WalletResponse]:
    """List all wallets."""
    wallets = db.query(WalletModel).all()
    return [
        WalletResponse(
            id=str(item.id),
            user_id=str(item.user_id),
            balance=Decimal(str(item.available_balance)),
            pending_withdrawal=Decimal('0.00'),
        )
        for item in wallets
    ]


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
    summary="Get wallet by ID",
    responses={404: {"description": "Wallet not found."}},
)
def get_wallet(wallet_id: str, db: Session = Depends(get_db)) -> WalletResponse:
    """Get one wallet by ID."""
    wallet = db.get(WalletModel, wallet_id)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return WalletResponse(
        id=str(wallet.id),
        user_id=str(wallet.user_id),
        balance=Decimal(str(wallet.available_balance)),
        pending_withdrawal=Decimal('0.00'),
    )


@router.patch(
    "/{wallet_id}",
    response_model=WalletResponse,
    summary="Update wallet",
    responses={404: {"description": "Wallet not found."}, 400: {"description": "Invalid update payload."}},
)
def update_wallet(wallet_id: str, payload: WalletUpdate, db: Session = Depends(get_db)) -> WalletResponse:
    """Patch a wallet."""
    wallet = db.get(WalletModel, wallet_id)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "balance":
            wallet.available_balance = float(value)
        elif key == "pending_withdrawal":
            pass

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return WalletResponse(
        id=str(wallet.id),
        user_id=str(wallet.user_id),
        balance=Decimal(str(wallet.available_balance)),
        pending_withdrawal=Decimal('0.00'),
    )


@router.delete(
    "/{wallet_id}",
    summary="Delete wallet",
    responses={404: {"description": "Wallet not found."}},
)
def delete_wallet(wallet_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a wallet by ID."""
    wallet = db.get(WalletModel, wallet_id)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    db.delete(wallet)
    db.commit()
    return {"detail": "Wallet deleted successfully"}

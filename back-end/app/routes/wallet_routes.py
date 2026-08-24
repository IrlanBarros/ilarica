"""Read-only authenticated wallet endpoint."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import UserModel, WalletModel
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.wallet_schemas import WalletResponse

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get(
    "/me",
    response_model=WalletResponse,
    responses={401: {"description": "Authentication required."}, 404: {"description": "Wallet not found."}},
)
def get_my_wallet(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> WalletResponse:
    """Return only the authenticated user's balance; clients cannot mutate balances."""
    wallet = db.query(WalletModel).filter(WalletModel.user_id == current_user.id).one_or_none()
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return WalletResponse(
        id=str(wallet.id),
        user_id=str(wallet.user_id),
        balance=Decimal(str(wallet.available_balance)),
        pending_withdrawal=Decimal("0.00"),
    )

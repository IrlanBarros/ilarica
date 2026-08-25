"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.models import UserModel
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.password_reset_schemas import PasswordResetConfirm, PasswordResetMessage, PasswordResetRequest
from app.services.password_reset_service import InvalidPasswordResetTokenError, PasswordResetService, PasswordResetUnavailableError
from app.schemas.email_verification_schemas import (
    EmailVerificationConfirm,
    EmailVerificationMessage,
    EmailVerificationRequest,
)
from app.services.email_verification_service import (
    EmailVerificationService,
    EmailVerificationUnavailableError,
    InvalidEmailVerificationTokenError,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=dict[str, str])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Authenticate a user and return an access token in OAuth2 format."""
    user_model = db.query(UserModel).filter(UserModel.email == form_data.username).one_or_none()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(db)
    try:
        token = auth_service.login_for_access_token(form_data.username, form_data.password)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/email-verification/request",
    response_model=EmailVerificationMessage,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_email_verification(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db),
) -> EmailVerificationMessage:
    try:
        EmailVerificationService(db).request(payload.email)
    except EmailVerificationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email verification is temporarily unavailable",
        ) from exc
    return EmailVerificationMessage(
        detail="If the account is pending, verification instructions were sent"
    )


@router.post("/email-verification/confirm", response_model=EmailVerificationMessage)
def confirm_email_verification(
    payload: EmailVerificationConfirm,
    db: Session = Depends(get_db),
) -> EmailVerificationMessage:
    try:
        EmailVerificationService(db).confirm(payload.token)
    except InvalidEmailVerificationTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return EmailVerificationMessage(detail="Email verified successfully")


@router.post("/password-reset/request", response_model=PasswordResetMessage, status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> PasswordResetMessage:
    try:
        PasswordResetService(db).request(payload.email)
    except PasswordResetUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Password recovery is temporarily unavailable") from exc
    return PasswordResetMessage(detail="If the account exists, recovery instructions were sent")


@router.post("/password-reset/confirm", response_model=PasswordResetMessage)
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)) -> PasswordResetMessage:
    try:
        PasswordResetService(db).confirm(payload.token, payload.password)
    except InvalidPasswordResetTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PasswordResetMessage(detail="Password updated successfully")

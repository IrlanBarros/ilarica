"""Security dependencies for protected endpoints."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.models import UserModel
from app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    """Return the authenticated user from a valid JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except Exception as exc:  # noqa: BLE001
        raise credentials_exception from exc

    user = db.query(UserModel).filter(UserModel.email == subject).one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def require_roles(*allowed_roles: str) -> Callable[..., UserModel]:
    """Build an authentication dependency restricted to explicit roles."""
    normalized_roles = frozenset(allowed_roles)

    def dependency(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        role = str(getattr(current_user, "role_type", getattr(current_user, "role", "")))
        if role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return dependency


require_admin = require_roles("admin")
require_customer = require_roles("customer")
require_canteen_staff = require_roles("canteen_staff")

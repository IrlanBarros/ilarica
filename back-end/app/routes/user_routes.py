"""User REST endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_admin
from app.database.session import get_db
from app.database.models import UserModel
from app.repositories.sqlalchemy_repositories import SQLAlchemyInvitationKeyRepository, SQLAlchemyUserRepository
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.services.email_verification_service import EmailVerificationService
from app.domain.access_identity.user import User

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


def _to_user_response(user: User | UserModel) -> UserResponse:
    """Map an authenticated or persisted user object into the public schema."""
    email = str(user.email)
    resolved_name = user.name
    resolved_role = getattr(user, "role", getattr(user, "role_type", "customer"))

    return UserResponse(
        id=user.id,
        name=resolved_name,
        email=email,
        whatsapp=user.whatsapp,
        role=str(resolved_role),
        is_active=user.is_active,
        is_email_validated=user.is_email_validated,
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    responses={
        201: {"description": "User created successfully."},
        400: {"description": "Invalid user payload or business rule failed."},
    },
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Create a new user in the platform."""
    if payload.role not in {"customer", "courier"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration only allows customer or courier roles",
        )

    service = UserService(SQLAlchemyUserRepository(db), SQLAlchemyInvitationKeyRepository(db))
    try:
        user = service.register(
            name=payload.name,
            email=payload.email,
            whatsapp=payload.whatsapp,
            password=payload.password,
            role=payload.role,
        )
        db.commit()
        try:
            EmailVerificationService(db).request(
                str(user.email), skip_if_unconfigured=True
            )
        except Exception:
            logger.exception("Unable to send registration verification email", extra={"user_id": str(user.id)})
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise

    return _to_user_response(user)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List users",
    responses={200: {"description": "List of users."}},
    dependencies=[Depends(require_admin)],
)
def list_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    """List all registered users."""
    users = db.query(UserModel).order_by(UserModel.created_at.desc()).all()
    return [_to_user_response(user) for user in users]


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={200: {"description": "Authenticated user profile."}, 401: {"description": "Unauthorized."}},
)
def get_current_user_profile(current_user: UserModel = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user without exposing sensitive fields."""
    return _to_user_response(current_user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    responses={
        200: {"description": "User found."},
        404: {"description": "User not found."},
    },
    dependencies=[Depends(require_admin)],
)
def get_user(user_id: UUID, db: Session = Depends(get_db)) -> UserResponse:
    """Get a single user by ID."""
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return _to_user_response(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    responses={
        200: {"description": "User updated successfully."},
        404: {"description": "User not found."},
        400: {"description": "Invalid update payload."},
    },
    dependencies=[Depends(require_admin)],
)
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
    """Update user fields using a partial payload."""
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    try:
        for key, value in updates.items():
            if key == "email":
                setattr(user, "email", value)
            elif key == "name":
                setattr(user, "name", value)
            elif key == "whatsapp":
                setattr(user, "whatsapp", value)
            elif key == "role":
                setattr(user, "role_type", value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_user_response(user)


@router.delete(
    "/{user_id}",
    summary="Delete user",
    responses={
        200: {"description": "User deleted successfully."},
        404: {"description": "User not found."},
    },
    dependencies=[Depends(require_admin)],
)
def delete_user(user_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a user by ID."""
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

"""User REST endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.database.models import UserModel
from app.repositories.sqlalchemy_repositories import SQLAlchemyInvitationKeyRepository, SQLAlchemyUserRepository
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _to_user_response(user: Any) -> UserResponse:
    """Map an authenticated or persisted user object into the public schema."""
    email = str(user.email)
    resolved_name = getattr(user, "name", email.split("@")[0])
    resolved_role = getattr(user, "role", getattr(user, "role_type", "customer"))
    resolved_is_active = bool(getattr(user, "is_active", True))

    return UserResponse(
        id=str(user.id),
        name=str(resolved_name),
        email=email,
        role=str(resolved_role),
        is_active=resolved_is_active,
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
    service = UserService(SQLAlchemyUserRepository(db), SQLAlchemyInvitationKeyRepository(db))
    try:
        user = service.register(payload.email, payload.password, role=payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserResponse(id=user.id, name=payload.name, email=user.email, role=user.role, is_active=user.is_active)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List users",
    responses={200: {"description": "List of users."}},
    dependencies=[Depends(get_current_user)],
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
    dependencies=[Depends(get_current_user)],
)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserResponse:
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
    dependencies=[Depends(get_current_user)],
)
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
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
    dependencies=[Depends(get_current_user)],
)
def delete_user(user_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a user by ID."""
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

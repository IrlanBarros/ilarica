"""Invitation key REST endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import InvitationKeyModel
from app.database.session import get_db
from app.schemas.invitation_key_schemas import InvitationKeyCreate, InvitationKeyResponse, InvitationKeyUpdate

router = APIRouter(prefix="/invitation-keys", tags=["Invitation Keys"])


@router.post(
    "/",
    response_model=InvitationKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create invitation key",
    responses={201: {"description": "Invitation key created successfully."}, 400: {"description": "Invalid invitation key payload."}},
)
def create_invitation_key(payload: InvitationKeyCreate, db: Session = Depends(get_db)) -> InvitationKeyResponse:
    """Create a new invitation key."""
    key = InvitationKeyModel(
        id=uuid4(),
        key_string=payload.key,
        is_used=payload.is_used,
        expires_at=payload.expires_at,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return InvitationKeyResponse(
        id=str(key.id),
        key=key.key_string,
        issued_to_email=payload.issued_to_email,
        expires_at=key.expires_at,
        is_used=key.is_used,
        is_expired=key.is_used,
    )


@router.get(
    "/",
    response_model=list[InvitationKeyResponse],
    summary="List invitation keys",
)
def list_invitation_keys(db: Session = Depends(get_db)) -> list[InvitationKeyResponse]:
    """List all invitation keys."""
    keys = db.query(InvitationKeyModel).all()
    return [
        InvitationKeyResponse(
            id=str(item.id),
            key=item.key_string,
            issued_to_email="",
            expires_at=item.expires_at,
            is_used=item.is_used,
            is_expired=item.is_used,
        )
        for item in keys
    ]


@router.get(
    "/{key_id}",
    response_model=InvitationKeyResponse,
    summary="Get invitation key by ID",
    responses={404: {"description": "Invitation key not found."}},
)
def get_invitation_key(key_id: str, db: Session = Depends(get_db)) -> InvitationKeyResponse:
    """Get one invitation key by ID."""
    key = db.get(InvitationKeyModel, key_id)
    if key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation key not found")
    return InvitationKeyResponse(
        id=str(key.id),
        key=key.key_string,
        issued_to_email="",
        expires_at=key.expires_at,
        is_used=key.is_used,
        is_expired=key.is_used,
    )


@router.patch(
    "/{key_id}",
    response_model=InvitationKeyResponse,
    summary="Update invitation key",
    responses={404: {"description": "Invitation key not found."}, 400: {"description": "Invalid update payload."}},
)
def update_invitation_key(key_id: str, payload: InvitationKeyUpdate, db: Session = Depends(get_db)) -> InvitationKeyResponse:
    """Patch an invitation key."""
    key = db.get(InvitationKeyModel, key_id)
    if key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation key not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "key":
            key.key_string = value
        elif field == "expires_at":
            key.expires_at = value
        elif field == "is_used":
            key.is_used = value
        elif field == "is_expired":
            key.is_used = value

    db.add(key)
    db.commit()
    db.refresh(key)
    return InvitationKeyResponse(
        id=str(key.id),
        key=key.key_string,
        issued_to_email="",
        expires_at=key.expires_at,
        is_used=key.is_used,
        is_expired=key.is_used,
    )


@router.delete(
    "/{key_id}",
    summary="Delete invitation key",
    responses={404: {"description": "Invitation key not found."}},
)
def delete_invitation_key(key_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete an invitation key by ID."""
    key = db.get(InvitationKeyModel, key_id)
    if key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation key not found")

    db.delete(key)
    db.commit()
    return {"detail": "Invitation key deleted successfully"}

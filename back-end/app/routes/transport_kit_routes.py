"""Transport kit REST endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import TransportKitModel
from app.database.session import get_db
from app.schemas.transport_kit_schemas import TransportKitCreate, TransportKitResponse, TransportKitUpdate

router = APIRouter(prefix="/transport-kits", tags=["Transport Kits"])


@router.post(
    "/",
    response_model=TransportKitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transport kit",
    responses={201: {"description": "Transport kit created successfully."}, 400: {"description": "Invalid transport kit payload."}},
)
def create_transport_kit(payload: TransportKitCreate, db: Session = Depends(get_db)) -> TransportKitResponse:
    """Create a new transport kit."""
    kit = TransportKitModel(
        id=uuid4(),
        courier_id=payload.courier_id,
        serial_number=payload.serial_number,
        is_allocated=payload.is_allocated,
    )
    db.add(kit)
    db.commit()
    db.refresh(kit)
    return TransportKitResponse(
        id=str(kit.id),
        serial_number=kit.serial_number,
        is_allocated=kit.is_allocated,
        courier_id=str(kit.courier_id) if kit.courier_id else None,
    )


@router.get(
    "/",
    response_model=list[TransportKitResponse],
    summary="List transport kits",
)
def list_transport_kits(db: Session = Depends(get_db)) -> list[TransportKitResponse]:
    """List all transport kits."""
    kits = db.query(TransportKitModel).all()
    return [
        TransportKitResponse(
            id=str(kit.id),
            serial_number=kit.serial_number,
            is_allocated=kit.is_allocated,
            courier_id=str(kit.courier_id) if kit.courier_id else None,
        )
        for kit in kits
    ]


@router.get(
    "/{kit_id}",
    response_model=TransportKitResponse,
    summary="Get transport kit by ID",
    responses={404: {"description": "Transport kit not found."}},
)
def get_transport_kit(kit_id: str, db: Session = Depends(get_db)) -> TransportKitResponse:
    """Get one transport kit by ID."""
    kit = db.get(TransportKitModel, kit_id)
    if kit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport kit not found")
    return TransportKitResponse(
        id=str(kit.id),
        serial_number=kit.serial_number,
        is_allocated=kit.is_allocated,
        courier_id=str(kit.courier_id) if kit.courier_id else None,
    )


@router.patch(
    "/{kit_id}",
    response_model=TransportKitResponse,
    summary="Update transport kit",
    responses={404: {"description": "Transport kit not found."}, 400: {"description": "Invalid update payload."}},
)
def update_transport_kit(kit_id: str, payload: TransportKitUpdate, db: Session = Depends(get_db)) -> TransportKitResponse:
    """Patch a transport kit."""
    kit = db.get(TransportKitModel, kit_id)
    if kit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport kit not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(kit, key, value)

    db.add(kit)
    db.commit()
    db.refresh(kit)
    return TransportKitResponse(
        id=str(kit.id),
        serial_number=kit.serial_number,
        is_allocated=kit.is_allocated,
        courier_id=str(kit.courier_id) if kit.courier_id else None,
    )


@router.delete(
    "/{kit_id}",
    summary="Delete transport kit",
    responses={404: {"description": "Transport kit not found."}},
)
def delete_transport_kit(kit_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a transport kit by ID."""
    kit = db.get(TransportKitModel, kit_id)
    if kit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport kit not found")

    db.delete(kit)
    db.commit()
    return {"detail": "Transport kit deleted successfully"}

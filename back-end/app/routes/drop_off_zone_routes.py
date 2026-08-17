"""Drop-off zone REST endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import DropOffZoneModel
from app.database.session import get_db
from app.schemas.drop_off_zone_schemas import DropOffZoneCreate, DropOffZoneResponse, DropOffZoneUpdate

router = APIRouter(prefix="/drop-off-zones", tags=["Drop-off Zones"])


@router.post(
    "/",
    response_model=DropOffZoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create drop-off zone",
    responses={201: {"description": "Drop-off zone created successfully."}, 400: {"description": "Invalid drop-off zone payload."}},
)
def create_drop_off_zone(payload: DropOffZoneCreate, db: Session = Depends(get_db)) -> DropOffZoneResponse:
    """Create a new drop-off zone."""
    zone = DropOffZoneModel(
        id=uuid4(),
        name=payload.name,
        description=None,
        capacity=payload.capacity_total,
        is_active=payload.is_active,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return DropOffZoneResponse(
        id=str(zone.id),
        name=zone.name,
        capacity_total=zone.capacity,
        current_load=0,
        is_active=zone.is_active,
    )


@router.get(
    "/",
    response_model=list[DropOffZoneResponse],
    summary="List drop-off zones",
)
def list_drop_off_zones(db: Session = Depends(get_db)) -> list[DropOffZoneResponse]:
    """List all drop-off zones."""
    zones = db.query(DropOffZoneModel).all()
    return [
        DropOffZoneResponse(
            id=str(zone.id),
            name=zone.name,
            capacity_total=zone.capacity,
            current_load=0,
            is_active=zone.is_active,
        )
        for zone in zones
    ]


@router.get(
    "/{zone_id}",
    response_model=DropOffZoneResponse,
    summary="Get drop-off zone by ID",
    responses={404: {"description": "Drop-off zone not found."}},
)
def get_drop_off_zone(zone_id: str, db: Session = Depends(get_db)) -> DropOffZoneResponse:
    """Get one drop-off zone by ID."""
    zone = db.get(DropOffZoneModel, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drop-off zone not found")
    return DropOffZoneResponse(
        id=str(zone.id),
        name=zone.name,
        capacity_total=zone.capacity,
        current_load=0,
        is_active=zone.is_active,
    )


@router.patch(
    "/{zone_id}",
    response_model=DropOffZoneResponse,
    summary="Update drop-off zone",
    responses={404: {"description": "Drop-off zone not found."}, 400: {"description": "Invalid update payload."}},
)
def update_drop_off_zone(zone_id: str, payload: DropOffZoneUpdate, db: Session = Depends(get_db)) -> DropOffZoneResponse:
    """Patch a drop-off zone."""
    zone = db.get(DropOffZoneModel, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drop-off zone not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "capacity_total":
            zone.capacity = value
        elif key == "is_active":
            zone.is_active = value
        elif key == "name":
            zone.name = value

    db.add(zone)
    db.commit()
    db.refresh(zone)
    return DropOffZoneResponse(
        id=str(zone.id),
        name=zone.name,
        capacity_total=zone.capacity,
        current_load=0,
        is_active=zone.is_active,
    )


@router.delete(
    "/{zone_id}",
    summary="Delete drop-off zone",
    responses={404: {"description": "Drop-off zone not found."}},
)
def delete_drop_off_zone(zone_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a drop-off zone by ID."""
    zone = db.get(DropOffZoneModel, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drop-off zone not found")

    db.delete(zone)
    db.commit()
    return {"detail": "Drop-off zone deleted successfully"}

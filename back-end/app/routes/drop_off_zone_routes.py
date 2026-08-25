"""Drop-off zone REST endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import DropOffZoneModel, OrderModel, OrderStatus
from app.database.session import get_db
from app.schemas.drop_off_zone_schemas import DropOffZoneCreate, DropOffZoneResponse, DropOffZoneUpdate

router = APIRouter(prefix="/drop-off-zones", tags=["Drop-off Zones"])


def _zone_response(db: Session, zone: DropOffZoneModel) -> DropOffZoneResponse:
    current_load = db.query(OrderModel).filter(
        OrderModel.drop_off_zone_id == zone.id,
        OrderModel.status != OrderStatus.COMPLETED,
    ).count()
    return DropOffZoneResponse(
        id=str(zone.id),
        name=zone.name,
        capacity_total=zone.capacity_total,
        current_load=current_load,
        is_active=zone.is_active,
    )


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
        capacity_total=payload.capacity_total,
        is_active=payload.is_active,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return _zone_response(db, zone)


@router.get(
    "/",
    response_model=list[DropOffZoneResponse],
    summary="List drop-off zones",
)
def list_drop_off_zones(db: Session = Depends(get_db)) -> list[DropOffZoneResponse]:
    """List all drop-off zones."""
    zones = db.query(DropOffZoneModel).order_by(DropOffZoneModel.name.asc()).all()
    return [_zone_response(db, zone) for zone in zones]


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
    return _zone_response(db, zone)


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
            zone.capacity_total = value
        elif key == "is_active":
            zone.is_active = value
        elif key == "name":
            zone.name = value

    db.add(zone)
    db.commit()
    db.refresh(zone)
    return _zone_response(db, zone)


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

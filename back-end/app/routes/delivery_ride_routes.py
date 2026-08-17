"""Delivery ride REST endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import DeliveryRideModel
from app.database.session import get_db
from app.schemas.delivery_ride_schemas import DeliveryRideCreate, DeliveryRideResponse, DeliveryRideUpdate

router = APIRouter(prefix="/delivery-rides", tags=["Delivery Rides"])


@router.post(
    "/",
    response_model=DeliveryRideResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create delivery ride",
    responses={201: {"description": "Delivery ride created successfully."}, 400: {"description": "Invalid delivery ride payload."}},
)
def create_delivery_ride(payload: DeliveryRideCreate, db: Session = Depends(get_db)) -> DeliveryRideResponse:
    """Create a new delivery ride."""
    ride = DeliveryRideModel(
        id=uuid4(),
        order_id=uuid4(),
        courier_id=payload.assigned_courier_id,
        status=payload.status,
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return DeliveryRideResponse(
        id=str(ride.id),
        drop_off_zone_id=str(ride.order_id),
        status=ride.status,
        assigned_courier_id=str(ride.courier_id) if ride.courier_id else None,
        is_arrived=False,
    )


@router.get(
    "/",
    response_model=list[DeliveryRideResponse],
    summary="List delivery rides",
)
def list_delivery_rides(db: Session = Depends(get_db)) -> list[DeliveryRideResponse]:
    """List all delivery rides."""
    rides = db.query(DeliveryRideModel).all()
    return [
        DeliveryRideResponse(
            id=str(ride.id),
            drop_off_zone_id=str(ride.order_id),
            status=ride.status,
            assigned_courier_id=str(ride.courier_id) if ride.courier_id else None,
            is_arrived=False,
        )
        for ride in rides
    ]


@router.get(
    "/{ride_id}",
    response_model=DeliveryRideResponse,
    summary="Get delivery ride by ID",
    responses={404: {"description": "Delivery ride not found."}},
)
def get_delivery_ride(ride_id: str, db: Session = Depends(get_db)) -> DeliveryRideResponse:
    """Get one delivery ride by ID."""
    ride = db.get(DeliveryRideModel, ride_id)
    if ride is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery ride not found")
    return DeliveryRideResponse(
        id=str(ride.id),
        drop_off_zone_id=str(ride.order_id),
        status=ride.status,
        assigned_courier_id=str(ride.courier_id) if ride.courier_id else None,
        is_arrived=False,
    )


@router.patch(
    "/{ride_id}",
    response_model=DeliveryRideResponse,
    summary="Update delivery ride",
    responses={404: {"description": "Delivery ride not found."}, 400: {"description": "Invalid update payload."}},
)
def update_delivery_ride(ride_id: str, payload: DeliveryRideUpdate, db: Session = Depends(get_db)) -> DeliveryRideResponse:
    """Patch a delivery ride."""
    ride = db.get(DeliveryRideModel, ride_id)
    if ride is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery ride not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(ride, key, value)

    db.add(ride)
    db.commit()
    db.refresh(ride)
    return DeliveryRideResponse(
        id=str(ride.id),
        drop_off_zone_id=str(ride.order_id),
        status=ride.status,
        assigned_courier_id=str(ride.courier_id) if ride.courier_id else None,
        is_arrived=False,
    )


@router.delete(
    "/{ride_id}",
    summary="Delete delivery ride",
    responses={404: {"description": "Delivery ride not found."}},
)
def delete_delivery_ride(ride_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a delivery ride by ID."""
    ride = db.get(DeliveryRideModel, ride_id)
    if ride is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery ride not found")

    db.delete(ride)
    db.commit()
    return {"detail": "Delivery ride deleted successfully"}

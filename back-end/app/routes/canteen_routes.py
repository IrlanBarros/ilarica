"""Canteen REST endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import CanteenModel
from app.database.session import get_db
from app.schemas.canteen_schemas import (
    CanteenCreate,
    CanteenResponse,
    CanteenUpdate,
)

router = APIRouter(prefix="/canteens", tags=["Canteens"])


@router.post(
    "/",
    response_model=CanteenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create canteen",
    responses={201: {"description": "Canteen created successfully."}, 400: {"description": "Invalid canteen payload."}},
)
def create_canteen(payload: CanteenCreate, db: Session = Depends(get_db)) -> CanteenResponse:
    """Create a new canteen."""
    canteen = CanteenModel(id=uuid4(), user_id=payload.user_id, is_open=payload.is_open)
    db.add(canteen)
    db.commit()
    db.refresh(canteen)
    return CanteenResponse(
        id=str(canteen.id),
        user_id=str(canteen.user_id),
        name=payload.name,
        location=payload.location,
        is_open=canteen.is_open,
        products=[],
    )


@router.get(
    "/",
    response_model=list[CanteenResponse],
    summary="List canteens",
)
def list_canteens(db: Session = Depends(get_db)) -> list[CanteenResponse]:
    """List all canteens."""
    canteens = db.query(CanteenModel).all()
    return [
        CanteenResponse(
            id=str(c.id),
            user_id=str(c.user_id),
            name=getattr(c, "name", ""),
            location=getattr(c, "location", ""),
            is_open=c.is_open,
            products=[],
        )
        for c in canteens
    ]


@router.get(
    "/{canteen_id}",
    response_model=CanteenResponse,
    summary="Get canteen by ID",
    responses={404: {"description": "Canteen not found."}},
)
def get_canteen(canteen_id: str, db: Session = Depends(get_db)) -> CanteenResponse:
    """Get a single canteen by ID."""
    c = db.get(CanteenModel, canteen_id)
    if c is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")
    return CanteenResponse(
        id=str(c.id),
        user_id=str(c.user_id),
        name=getattr(c, "name", ""),
        location=getattr(c, "location", ""),
        is_open=c.is_open,
        products=[],
    )


@router.patch(
    "/{canteen_id}",
    response_model=CanteenResponse,
    summary="Update canteen",
    responses={404: {"description": "Canteen not found."}, 400: {"description": "Invalid update payload."}},
)
def update_canteen(canteen_id: str, payload: CanteenUpdate, db: Session = Depends(get_db)) -> CanteenResponse:
    """Partially update canteen fields."""
    c = db.get(CanteenModel, canteen_id)
    if c is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "is_open":
            setattr(c, "is_open", value)
        # name/location/products are not stored on the current model; ignore but reflect in response

    db.add(c)
    db.commit()
    db.refresh(c)
    return CanteenResponse(
        id=str(c.id),
        user_id=str(c.user_id),
        name=updates.get("name", getattr(c, "name", "")),
        location=updates.get("location", getattr(c, "location", "")),
        is_open=c.is_open,
        products=updates.get("products", []),
    )


@router.delete(
    "/{canteen_id}",
    summary="Delete canteen",
    responses={404: {"description": "Canteen not found."}},
)
def delete_canteen(canteen_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a canteen by ID."""
    c = db.get(CanteenModel, canteen_id)
    if c is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")

    db.delete(c)
    db.commit()
    return {"detail": "Canteen deleted successfully"}

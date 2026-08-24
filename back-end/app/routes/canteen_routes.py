"""Canteen REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.use_cases.manage_canteens import (
    CreateCanteenUseCase,
    GetCanteenUseCase,
    ListCanteensUseCase,
    UpdateCanteenUseCase,
)
from app.database.models import CanteenModel
from app.domain.catalog.canteen import Canteen
from app.database.session import get_db
from app.repositories.sqlalchemy_repositories import SQLAlchemyCanteenRepository
from app.schemas.canteen_schemas import (
    CanteenCreate,
    CanteenResponse,
    CanteenUpdate,
)

router = APIRouter(prefix="/canteens", tags=["Canteens"])


def _to_response(canteen: Canteen) -> CanteenResponse:
    return CanteenResponse(
        id=UUID(canteen.id),
        user_id=UUID(canteen.user_id),
        name=canteen.name,
        location=canteen.location,
        is_open=canteen.is_open,
        products=[UUID(product_id) for product_id in canteen.products],
    )


@router.post(
    "/",
    response_model=CanteenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create canteen",
    responses={201: {"description": "Canteen created successfully."}, 400: {"description": "Invalid canteen payload."}},
)
def create_canteen(payload: CanteenCreate, db: Session = Depends(get_db)) -> CanteenResponse:
    """Create a new canteen."""
    use_case = CreateCanteenUseCase(SQLAlchemyCanteenRepository(db))
    try:
        canteen = use_case.execute(
            user_id=str(payload.user_id),
            name=payload.name,
            location=payload.location,
            is_open=payload.is_open,
        )
        db.commit()
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid canteen data or owner identifier",
        ) from exc
    except Exception:
        db.rollback()
        raise
    return _to_response(canteen)


@router.get(
    "/",
    response_model=list[CanteenResponse],
    summary="List canteens",
)
def list_canteens(db: Session = Depends(get_db)) -> list[CanteenResponse]:
    """List all canteens."""
    canteens = ListCanteensUseCase(SQLAlchemyCanteenRepository(db)).execute()
    return [_to_response(canteen) for canteen in canteens]


@router.get(
    "/{canteen_id}",
    response_model=CanteenResponse,
    summary="Get canteen by ID",
    responses={404: {"description": "Canteen not found."}},
)
def get_canteen(canteen_id: UUID, db: Session = Depends(get_db)) -> CanteenResponse:
    """Get a single canteen by ID."""
    canteen = GetCanteenUseCase(SQLAlchemyCanteenRepository(db)).execute(str(canteen_id))
    if canteen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")
    return _to_response(canteen)


@router.patch(
    "/{canteen_id}",
    response_model=CanteenResponse,
    summary="Update canteen",
    responses={404: {"description": "Canteen not found."}, 400: {"description": "Invalid update payload."}},
)
def update_canteen(canteen_id: UUID, payload: CanteenUpdate, db: Session = Depends(get_db)) -> CanteenResponse:
    """Partially update canteen fields."""
    updates = payload.model_dump(exclude_unset=True)
    use_case = UpdateCanteenUseCase(SQLAlchemyCanteenRepository(db))
    try:
        canteen = use_case.execute(str(canteen_id), **updates)
        if canteen is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return _to_response(canteen)


@router.delete(
    "/{canteen_id}",
    summary="Delete canteen",
    responses={404: {"description": "Canteen not found."}},
)
def delete_canteen(canteen_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a canteen by ID."""
    c = db.get(CanteenModel, canteen_id)
    if c is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")

    db.delete(c)
    db.commit()
    return {"detail": "Canteen deleted successfully"}

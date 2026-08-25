"""Canteen REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.application.use_cases.manage_canteens import (
    CreateCanteenUseCase,
    GetCanteenUseCase,
    ListCanteensUseCase,
    UpdateCanteenUseCase,
)
from app.database.models import CanteenModel, OrderItemModel, OrderModel, OrderStatus, UserModel
from app.dependencies.auth import get_current_user
from app.domain.exceptions import InvalidOrderStatusTransitionError
from app.domain.order.order import Order
from app.domain.catalog.canteen import Canteen
from app.database.session import get_db
from app.repositories.sqlalchemy_repositories import SQLAlchemyCanteenRepository
from app.schemas.canteen_schemas import (
    CanteenCreate,
    CanteenResponse,
    CanteenUpdate,
)
from app.schemas.order_schemas import (
    SellerOrderCustomerResponse,
    SellerOrderDestinationResponse,
    SellerOrderItemResponse,
    SellerOrderResponse,
    SellerOrderStatusUpdate,
)

router = APIRouter(prefix="/canteens", tags=["Canteens"])


def _current_role(current_user: UserModel) -> str:
    return str(getattr(current_user, "role_type", getattr(current_user, "role", "")))


def _order_status_value(order: OrderModel) -> str:
    return order.status.value if isinstance(order.status, OrderStatus) else str(order.status)


def _owned_canteen(db: Session, current_user: UserModel) -> CanteenModel:
    if _current_role(current_user) != "canteen_staff":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Canteen staff access required")
    canteen = db.query(CanteenModel).filter(CanteenModel.user_id == current_user.id).one_or_none()
    if canteen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found for authenticated user")
    return canteen


def _seller_order_response(order: OrderModel) -> SellerOrderResponse:
    return SellerOrderResponse(
        id=order.id,
        canteen_id=order.canteen_id,
        status=_order_status_value(order),
        items=[
            SellerOrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ],
        total_amount=order.total_amount,
        customer=SellerOrderCustomerResponse(id=order.customer.id, name=order.customer.name),
        destination=SellerOrderDestinationResponse(
            id=order.drop_off_zone.id,
            name=order.drop_off_zone.name,
            description=order.drop_off_zone.description,
        ),
    )


def _seller_order_query(db: Session):
    return db.query(OrderModel).options(
        selectinload(OrderModel.customer),
        selectinload(OrderModel.drop_off_zone),
        selectinload(OrderModel.items).selectinload(OrderItemModel.product),
    )


@router.get("/me/orders", response_model=list[SellerOrderResponse], summary="List authenticated canteen orders")
def list_my_canteen_orders(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> list[SellerOrderResponse]:
    """Return only operational orders owned by the authenticated staff canteen."""
    canteen = _owned_canteen(db, current_user)
    orders = _seller_order_query(db).filter(
        OrderModel.canteen_id == canteen.id,
        OrderModel.status.in_([OrderStatus.PAID.value, OrderStatus.PREPARING.value, OrderStatus.READY_FOR_PICKUP.value]),
    ).order_by(OrderModel.id.asc()).all()
    return [_seller_order_response(order) for order in orders]


@router.patch(
    "/me/orders/{order_id}/status",
    response_model=SellerOrderResponse,
    summary="Advance an authenticated canteen order",
)
def update_my_canteen_order_status(
    order_id: UUID,
    payload: SellerOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SellerOrderResponse:
    """Advance exactly one canteen fulfillment state and commit atomically."""
    canteen = _owned_canteen(db, current_user)
    order = _seller_order_query(db).filter(
        OrderModel.id == order_id,
        OrderModel.canteen_id == canteen.id,
    ).with_for_update().one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    aggregate = Order(
        id=str(order.id),
        user_id=str(order.customer_id),
        canteen_id=str(order.canteen_id),
        drop_off_zone_id=str(order.drop_off_zone_id),
        status=_order_status_value(order),
        is_paid=True,
    )
    try:
        aggregate.advance_canteen_fulfillment(payload.status)
        order.status = OrderStatus(aggregate.status)
        db.add(order)
        db.commit()
        db.refresh(order)
    except InvalidOrderStatusTransitionError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return _seller_order_response(order)


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

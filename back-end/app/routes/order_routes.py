"""Order REST endpoints."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database.models import OrderItemModel, OrderModel, UserModel
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin, require_customer
from app.schemas.order_schemas import (
    CustomerOrderCanteenResponse, CustomerOrderResponse, OrderCreate, OrderItemResponse,
    OrderResponse, OrderUpdate, SellerOrderDestinationResponse, SellerOrderItemResponse,
)
from app.services.order_creation_service import CreatedOrder, OrderCreationError, OrderCreationService

router = APIRouter(prefix="/orders", tags=["Orders"])


def _order_response(order: OrderModel | CreatedOrder, *, include_pin: bool = True) -> OrderResponse:
    return OrderResponse(
        id=str(order.id),
        customer_id=str(order.customer_id),
        canteen_id=str(order.canteen_id),
        drop_off_zone_id=str(order.drop_off_zone_id) if order.drop_off_zone_id else None,
        fulfillment_type=order.fulfillment_type,
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        total_amount=Decimal(str(order.total_amount)),
        items=[
            OrderItemResponse(
                id=str(item.id),
                product_id=str(item.product_id),
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
            )
            for item in order.items
        ],
        pickup_pin=order.pickup_pin if include_pin else None,
    )


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    responses={
        201: {"description": "Order created successfully."},
        400: {"description": "Invalid order payload."},
        401: {"description": "Authentication required."},
        403: {"description": "The customer does not match the authenticated user."},
        404: {"description": "A referenced product was not found."},
        409: {"description": "Canteen, product or drop-off zone unavailable."},
    },
)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_customer),
) -> OrderResponse:
    """Create a new order with one or more items."""
    try:
        order = OrderCreationService(db).create(
            authenticated_customer_id=current_user.id,
            customer_id=payload.customer_id,
            canteen_id=payload.canteen_id,
            fulfillment_type=payload.fulfillment_type,
            drop_off_zone_id=payload.drop_off_zone_id,
            items=[(item.product_id, item.quantity) for item in payload.items],
        )
    except OrderCreationError as exc:
        status_by_code = {
            "forbidden": status.HTTP_403_FORBIDDEN,
            "not_found": status.HTTP_404_NOT_FOUND,
            "conflict": status.HTTP_409_CONFLICT,
            "invalid_uuid": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "invalid": status.HTTP_400_BAD_REQUEST,
        }
        raise HTTPException(status_code=status_by_code[exc.code], detail=str(exc)) from exc
    return _order_response(order)


@router.get("/me", response_model=list[CustomerOrderResponse], summary="List authenticated customer orders")
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_customer),
) -> list[CustomerOrderResponse]:
    orders = db.query(OrderModel).options(
        selectinload(OrderModel.canteen),
        selectinload(OrderModel.drop_off_zone),
        selectinload(OrderModel.items).selectinload(OrderItemModel.product),
    ).filter(OrderModel.customer_id == current_user.id).order_by(OrderModel.id.desc()).all()
    return [
        CustomerOrderResponse(
            id=order.id,
            canteen_id=order.canteen_id,
            status=order.status.value if hasattr(order.status, "value") else str(order.status),
            fulfillment_type=order.fulfillment_type,
            items=[SellerOrderItemResponse(
                id=item.id, product_id=item.product_id, name=item.product.name,
                quantity=item.quantity, unit_price=item.unit_price,
            ) for item in order.items],
            total_amount=order.total_amount,
            destination=SellerOrderDestinationResponse(
                id=order.drop_off_zone.id, name=order.drop_off_zone.name,
                description=order.drop_off_zone.description,
            ) if order.drop_off_zone else None,
            canteen=CustomerOrderCanteenResponse(
                id=order.canteen.id, name=order.canteen.name, location=order.canteen.location,
            ),
            pickup_pin=order.pickup_pin if order.fulfillment_type == "pickup" else None,
        ) for order in orders
    ]


@router.get(
    "/",
    response_model=list[OrderResponse],
    summary="List orders",
)
def list_orders(
    db: Session = Depends(get_db),
    _: UserModel = Depends(require_admin),
) -> list[OrderResponse]:
    """List all orders for administrators only."""
    orders = db.query(OrderModel).options(selectinload(OrderModel.items)).order_by(OrderModel.id.asc()).all()
    return [_order_response(order) for order in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    responses={404: {"description": "Order not found."}},
)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> OrderResponse:
    """Get an order only when owned by the authenticated customer or an administrator."""
    order = db.query(OrderModel).options(selectinload(OrderModel.items)).filter(OrderModel.id == order_id).one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    role = str(getattr(current_user, "role_type", getattr(current_user, "role", "")))
    if role != "admin" and (role != "customer" or order.customer_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this order")
    return _order_response(order)


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order",
    responses={404: {"description": "Order not found."}},
)
def update_order(order_id: str, payload: OrderUpdate, db: Session = Depends(get_db), _: UserModel = Depends(require_admin)) -> OrderResponse:
    """Partially update order fields."""
    order = db.get(OrderModel, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(order, key, value)

    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderResponse(
        id=str(order.id),
        customer_id=str(order.customer_id),
        canteen_id=str(order.canteen_id),
        drop_off_zone_id=str(order.drop_off_zone_id) if order.drop_off_zone_id else None,
        fulfillment_type=order.fulfillment_type,
        status=str(order.status),
        total_amount=Decimal(str(order.total_amount)),
        items=[],
        pickup_pin=order.pickup_pin,
    )


@router.delete(
    "/{order_id}",
    summary="Delete order",
    responses={404: {"description": "Order not found."}},
)
def delete_order(order_id: str, db: Session = Depends(get_db), _: UserModel = Depends(require_admin)) -> dict[str, str]:
    """Delete an order by ID."""
    order = db.get(OrderModel, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"detail": "Order deleted successfully"}

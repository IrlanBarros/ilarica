"""Order REST endpoints."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import CanteenModel, DropOffZoneModel, OrderModel, ProductModel, UserModel
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem
from app.repositories.sqlalchemy_repositories import (
    SQLAlchemyOrderRepository,
    SQLAlchemyProductRepository,
    SQLAlchemyWalletRepository,
)
from app.schemas.order_schemas import OrderCreate, OrderItemResponse, OrderResponse, OrderUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


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
    current_user: UserModel = Depends(get_current_user),
) -> OrderResponse:
    """Create a new order with one or more items."""
    if payload.customer_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The order customer must match the authenticated user")

    try:
        canteen_uuid = UUID(payload.canteen_id)
        zone_uuid = UUID(payload.drop_off_zone_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid UUID in order payload") from exc

    canteen = db.get(CanteenModel, canteen_uuid)
    if canteen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")
    if not canteen.is_open:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The selected canteen is currently unavailable")

    zone = db.get(DropOffZoneModel, zone_uuid)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drop-off zone not found")
    if not zone.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The selected drop-off zone is unavailable")
    current_zone_load = db.query(OrderModel).filter(OrderModel.drop_off_zone_id == zone.id, OrderModel.status != "completed").count()
    if current_zone_load >= zone.capacity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The selected drop-off zone is at capacity")

    service = OrderService(SQLAlchemyOrderRepository(db), SQLAlchemyProductRepository(db), SQLAlchemyWalletRepository(db))
    order_items: list[OrderItem] = []
    for item in payload.items:
        try:
            product_uuid = UUID(item.product_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid product UUID") from exc
        product = db.get(ProductModel, product_uuid)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{item.product_id}' not found",
            )
        if str(product.canteen_id) != payload.canteen_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All products must belong to the selected canteen")
        if not product.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Product '{product.name}' is unavailable")
        order_items.append(
            OrderItem(
                product_id=item.product_id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(product.price)),
            )
        )

    total = sum((item.calculateSubtotal() for item in order_items), Decimal("0"))
    order = Order(
        id=str(uuid4()),
        user_id=payload.customer_id,
        canteen_id=payload.canteen_id,
        drop_off_zone_id=payload.drop_off_zone_id,
        items=order_items,
        status="draft",
        is_paid=False,
    )
    try:
        saved = service.create_order(order)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return OrderResponse(
        id=saved.id,
        customer_id=payload.customer_id,
        canteen_id=payload.canteen_id,
        drop_off_zone_id=payload.drop_off_zone_id,
        status=saved.status,
        total_amount=total,
        items=[
            OrderItemResponse(
                id=str(uuid4()),
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order_items
        ],
        pickup_pin=None,
    )


@router.get(
    "/",
    response_model=list[OrderResponse],
    summary="List orders",
)
def list_orders(db: Session = Depends(get_db)) -> list[OrderResponse]:
    """List all orders."""
    orders = db.query(OrderModel).order_by(OrderModel.id.asc()).all()
    return [
        OrderResponse(
            id=str(order.id),
            customer_id=str(order.customer_id),
            canteen_id=str(order.canteen_id),
            drop_off_zone_id=str(order.drop_off_zone_id),
            status=str(order.status),
            total_amount=Decimal(str(order.total_amount)),
            items=[],
            pickup_pin=order.pickup_pin,
        )
        for order in orders
    ]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    responses={404: {"description": "Order not found."}},
)
def get_order(order_id: str, db: Session = Depends(get_db)) -> OrderResponse:
    """Get a single order by ID."""
    order = db.get(OrderModel, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return OrderResponse(
        id=str(order.id),
        customer_id=str(order.customer_id),
        canteen_id=str(order.canteen_id),
        drop_off_zone_id=str(order.drop_off_zone_id),
        status=str(order.status),
        total_amount=Decimal(str(order.total_amount)),
        items=[],
        pickup_pin=order.pickup_pin,
    )


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order",
    responses={404: {"description": "Order not found."}},
)
def update_order(order_id: str, payload: OrderUpdate, db: Session = Depends(get_db)) -> OrderResponse:
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
        drop_off_zone_id=str(order.drop_off_zone_id),
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
def delete_order(order_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete an order by ID."""
    order = db.get(OrderModel, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"detail": "Order deleted successfully"}

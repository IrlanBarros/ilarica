"""Order REST endpoints."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import OrderModel, ProductModel
from app.database.session import get_db
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
        404: {"description": "A referenced product was not found."},
    },
)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderResponse:
    """Create a new order with one or more items."""
    service = OrderService(SQLAlchemyOrderRepository(db), SQLAlchemyProductRepository(db), SQLAlchemyWalletRepository(db))
    order_items: list[OrderItem] = []
    for item in payload.items:
        product = db.get(ProductModel, item.product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{item.product_id}' not found",
            )
        order_items.append(
            OrderItem(
                product_id=item.product_id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
            )
        )

    total = sum((item.calculateSubtotal() for item in order_items), Decimal("0"))
    order = Order(id=str(uuid4()), user_id=payload.customer_id, items=order_items, status="draft", is_paid=False)
    try:
        saved = service.create_order(order)
    except ValueError as exc:
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

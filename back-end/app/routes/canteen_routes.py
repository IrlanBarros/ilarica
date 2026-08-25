"""Canteen REST endpoints."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal, cast
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
from app.database.models import CanteenModel, OrderItemModel, OrderModel, OrderStatus, ProductModel, UserModel
from app.dependencies.auth import require_admin, require_canteen_staff
from app.domain.exceptions import InvalidOrderStatusTransitionError, InvalidPinError
from app.domain.order.order import Order
from app.domain.catalog.canteen import Canteen
from app.database.session import get_db
from app.repositories.sqlalchemy_repositories import SQLAlchemyCanteenRepository
from app.schemas.canteen_schemas import (
    BusinessHoursEntry,
    CanteenCreate,
    CanteenResponse,
    CanteenUpdate,
)
from app.schemas.product_schemas import ProductBase, ProductCategory, ProductResponse, ProductUpdate
from app.schemas.order_schemas import (
    SellerOrderCustomerResponse,
    SellerOrderDestinationResponse,
    SellerOrderItemResponse,
    SellerOrderResponse,
    SellerOrderStatusUpdate,
    SellerPickupConfirmation,
    SellerPickupConfirmationResponse,
)

router = APIRouter(prefix="/canteens", tags=["Canteens"])


SellerOrderStatus = Literal["paid", "preparing", "ready_for_pickup", "completed"]
FulfillmentType = Literal["pickup", "delivery"]


def _order_status_value(order: OrderModel) -> SellerOrderStatus:
    value = order.status.value if isinstance(order.status, OrderStatus) else str(order.status)
    return cast(SellerOrderStatus, value)


def _owned_canteen(db: Session, current_user: UserModel) -> CanteenModel:
    canteen = db.query(CanteenModel).filter(CanteenModel.user_id == current_user.id).one_or_none()
    if canteen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found for authenticated user")
    return canteen


def _seller_order_response(order: OrderModel) -> SellerOrderResponse:
    return SellerOrderResponse(
        id=UUID(str(order.id)),
        canteen_id=UUID(str(order.canteen_id)),
        status=_order_status_value(order),
        items=[
            SellerOrderItemResponse(
                id=UUID(str(item.id)),
                product_id=UUID(str(item.product_id)),
                name=item.product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
            )
            for item in order.items
        ],
        total_amount=Decimal(str(order.total_amount)),
        customer=SellerOrderCustomerResponse(id=order.customer.id, name=order.customer.name),
        destination=SellerOrderDestinationResponse(
            id=UUID(str(order.drop_off_zone.id)),
            name=order.drop_off_zone.name,
            description=order.drop_off_zone.description,
        ) if order.drop_off_zone else None,
        fulfillment_type=cast(FulfillmentType, order.fulfillment_type),
    )


def _seller_order_query(db: Session):
    return db.query(OrderModel).options(
        selectinload(OrderModel.customer),
        selectinload(OrderModel.drop_off_zone),
        selectinload(OrderModel.items).selectinload(OrderItemModel.product),
    )


def _product_response(product: ProductModel) -> ProductResponse:
    return ProductResponse(
        id=str(product.id), canteen_id=str(product.canteen_id), name=product.name,
        description=product.description, image_url=product.image_url,
        category=cast(ProductCategory, product.category), price=Decimal(str(product.price)),
        stock_quantity=product.stock_quantity,
        is_active=product.is_active, is_fast_stock_enabled=product.is_fast_stock_enabled,
    )


@router.get("/me", response_model=CanteenResponse, summary="Get authenticated staff canteen")
def get_my_canteen(
    db: Session = Depends(get_db), current_user: UserModel = Depends(require_canteen_staff)
) -> CanteenResponse:
    return CanteenResponse.model_validate(_owned_canteen(db, current_user))


@router.patch("/me", response_model=CanteenResponse, summary="Update authenticated staff canteen")
def update_my_canteen(
    payload: CanteenUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> CanteenResponse:
    canteen = _owned_canteen(db, current_user)
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(canteen, key, value)
    db.add(canteen)
    db.commit()
    db.refresh(canteen)
    return CanteenResponse.model_validate(canteen)


@router.get("/me/products", response_model=list[ProductResponse], summary="List authenticated canteen products")
def list_my_products(
    db: Session = Depends(get_db), current_user: UserModel = Depends(require_canteen_staff)
) -> list[ProductResponse]:
    canteen = _owned_canteen(db, current_user)
    products = db.query(ProductModel).filter(ProductModel.canteen_id == canteen.id).order_by(ProductModel.name).all()
    return [_product_response(product) for product in products]


@router.post("/me/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_my_product(
    payload: ProductBase,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> ProductResponse:
    canteen = _owned_canteen(db, current_user)
    product = ProductModel(canteen_id=canteen.id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return _product_response(product)


def _owned_product(db: Session, canteen: CanteenModel, product_id: UUID) -> ProductModel:
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id, ProductModel.canteen_id == canteen.id
    ).one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.patch("/me/products/{product_id}", response_model=ProductResponse)
def update_my_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> ProductResponse:
    canteen = _owned_canteen(db, current_user)
    product = _owned_product(db, canteen, product_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return _product_response(product)


@router.delete("/me/products/{product_id}")
def delete_my_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> dict[str, str]:
    canteen = _owned_canteen(db, current_user)
    product = _owned_product(db, canteen, product_id)
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}


@router.get("/me/orders", response_model=list[SellerOrderResponse], summary="List authenticated canteen orders")
def list_my_canteen_orders(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> list[SellerOrderResponse]:
    """Return only operational orders owned by the authenticated staff canteen."""
    canteen = _owned_canteen(db, current_user)
    orders = _seller_order_query(db).filter(
        OrderModel.canteen_id == canteen.id,
        OrderModel.status.in_([OrderStatus.PAID.value, OrderStatus.PREPARING.value, OrderStatus.READY_FOR_PICKUP.value]),
    ).order_by(OrderModel.id.asc()).all()
    return [_seller_order_response(order) for order in orders]


@router.get("/me/orders/history", response_model=list[SellerOrderResponse], summary="List authenticated canteen order history")
def list_my_canteen_order_history(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> list[SellerOrderResponse]:
    """Return only completed orders owned by the authenticated staff canteen."""
    canteen = _owned_canteen(db, current_user)
    orders = _seller_order_query(db).filter(
        OrderModel.canteen_id == canteen.id,
        OrderModel.status == OrderStatus.COMPLETED.value,
    ).order_by(OrderModel.id.desc()).all()
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
    current_user: UserModel = Depends(require_canteen_staff),
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
        drop_off_zone_id=str(order.drop_off_zone_id) if order.drop_off_zone_id else None,
        fulfillment_type=order.fulfillment_type,
        status=_order_status_value(order),
        is_paid=True,
    )
    try:
        aggregate.advance_canteen_fulfillment(payload.status)
        order.status = OrderStatus(aggregate.status)
        if aggregate.status == Order.STATUS_READY_FOR_PICKUP and order.fulfillment_type == "pickup":
            aggregate.generate_pickup_pin()
            order.pickup_pin = aggregate.pickup_pin
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


@router.post(
    "/me/orders/{order_id}/pickup/confirm",
    response_model=SellerPickupConfirmationResponse,
    summary="Confirm pickup using the customer PIN",
)
def confirm_my_canteen_order_pickup(
    order_id: UUID,
    payload: SellerPickupConfirmation,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_canteen_staff),
) -> SellerPickupConfirmationResponse:
    """Complete an owned pickup exactly once while holding a row-level lock."""
    canteen = _owned_canteen(db, current_user)
    order = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.canteen_id == canteen.id,
    ).with_for_update().one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    current_status = _order_status_value(order)
    if order.fulfillment_type != "pickup":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pickup orders can be confirmed with a PIN")
    if current_status == Order.STATUS_COMPLETED:
        if order.pickup_pin == payload.pickup_pin:
            return SellerPickupConfirmationResponse(id=UUID(str(order.id)), status="completed")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid pickup PIN")
    if current_status != Order.STATUS_READY_FOR_PICKUP:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order is not ready for pickup")

    aggregate = Order(
        id=str(order.id), user_id=str(order.customer_id), canteen_id=str(order.canteen_id),
        fulfillment_type=order.fulfillment_type, status=current_status, is_paid=True,
        pickup_pin=order.pickup_pin,
    )
    try:
        aggregate.complete_order(payload.pickup_pin)
        order.status = OrderStatus.COMPLETED
        db.add(order)
        db.commit()
    except (InvalidPinError, InvalidOrderStatusTransitionError) as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return SellerPickupConfirmationResponse(id=UUID(str(order.id)), status="completed")


def _to_response(canteen: Canteen) -> CanteenResponse:
    return CanteenResponse(
        id=UUID(canteen.id),
        user_id=UUID(canteen.user_id),
        name=canteen.name,
        location=canteen.location,
        is_open=canteen.is_open,
        products=[UUID(product_id) for product_id in canteen.products],
        opening_hours=[BusinessHoursEntry.model_validate(entry) for entry in canteen.opening_hours],
    )


@router.post(
    "/",
    response_model=CanteenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create canteen",
    responses={201: {"description": "Canteen created successfully."}, 400: {"description": "Invalid canteen payload."}},
)
def create_canteen(payload: CanteenCreate, db: Session = Depends(get_db), _: UserModel = Depends(require_admin)) -> CanteenResponse:
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
def update_canteen(canteen_id: UUID, payload: CanteenUpdate, db: Session = Depends(get_db), _: UserModel = Depends(require_admin)) -> CanteenResponse:
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
def delete_canteen(canteen_id: UUID, db: Session = Depends(get_db), _: UserModel = Depends(require_admin)) -> dict[str, str]:
    """Delete a canteen by ID."""
    c = db.get(CanteenModel, canteen_id)
    if c is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canteen not found")

    db.delete(c)
    db.commit()
    return {"detail": "Canteen deleted successfully"}

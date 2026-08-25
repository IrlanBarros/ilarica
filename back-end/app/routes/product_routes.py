"""Product REST endpoints."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import ProductModel, UserModel
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.repositories.sqlalchemy_repositories import SQLAlchemyProductRepository
from app.schemas.product_schemas import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService
from app.domain.catalog.product import Product

router = APIRouter(prefix="/products", tags=["Products"])


def _require_admin(current_user: UserModel) -> None:
    role = str(getattr(current_user, "role_type", getattr(current_user, "role", "")))
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    responses={
        201: {"description": "Product created successfully."},
        400: {"description": "Invalid product payload."},
    },
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> ProductResponse:
    """Create a new product for a canteen."""
    _require_admin(current_user)
    service = ProductService(SQLAlchemyProductRepository(db))

    product = Product(
        id=str(uuid4()),
        name=payload.name,
        price=Decimal(str(payload.price)),
        is_active=payload.is_active,
        stock_quantity=0,
        is_fast_stock_enabled=False,
        canteen_id=payload.canteen_id,
        description=payload.description,
        image_url=payload.image_url,
    )

    try:
        saved = service.create(product)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ProductResponse(
        id=saved.id,
        name=saved.name,
        description=payload.description,
        image_url=payload.image_url,
        price=saved.price,
        is_active=saved.is_active,
        canteen_id=payload.canteen_id,
        is_fast_stock_enabled=saved.is_fast_stock_enabled,
    )


@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="List products",
)
def list_products(db: Session = Depends(get_db)) -> list[ProductResponse]:
    """List all products."""
    products = db.query(ProductModel).order_by(ProductModel.name.asc()).all()
    return [
        ProductResponse(
            id=str(product.id),
            name=product.name,
            description=product.description,
            image_url=product.image_url,
            price=Decimal(str(product.price)),
            is_active=product.is_active,
            canteen_id=str(product.canteen_id),
            is_fast_stock_enabled=product.is_fast_stock_enabled,
        )
        for product in products
    ]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    responses={404: {"description": "Product not found."}},
)
def get_product(product_id: str, db: Session = Depends(get_db)) -> ProductResponse:
    """Get a product by ID."""
    product = db.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return ProductResponse(
        id=str(product.id),
        name=product.name,
        description=product.description,
        image_url=product.image_url,
        price=Decimal(str(product.price)),
        is_active=product.is_active,
        canteen_id=str(product.canteen_id),
        is_fast_stock_enabled=product.is_fast_stock_enabled,
    )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    responses={404: {"description": "Product not found."}},
)
def update_product(product_id: str, payload: ProductUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> ProductResponse:
    """Update product data using a partial payload."""
    _require_admin(current_user)
    product = db.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(product, key, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse(
        id=str(product.id),
        name=product.name,
        description=product.description,
        image_url=product.image_url,
        price=Decimal(str(product.price)),
        is_active=product.is_active,
        canteen_id=str(product.canteen_id),
        is_fast_stock_enabled=product.is_fast_stock_enabled,
    )


@router.delete(
    "/{product_id}",
    summary="Delete product",
    responses={404: {"description": "Product not found."}},
)
def delete_product(product_id: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> dict[str, str]:
    """Delete a product by ID."""
    _require_admin(current_user)
    product = db.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}

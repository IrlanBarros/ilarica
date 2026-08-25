from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.models import CanteenModel, DropOffZoneModel, OrderModel, ProductModel, UserModel
from app.domain.access_identity.user import User
from app.routes.order_routes import create_order
from app.schemas.order_schemas import OrderCreate


AUTH_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def _catalog(
    db_session: Session,
    *,
    product_active: bool = True,
    opening_hours: list[dict[str, object]] | None = None,
) -> tuple[str, str, str]:
    staff = UserModel(
        id=uuid4(),
        name="Cantina QA",
        email=f"staff-{uuid4()}@example.com",
        whatsapp="5588999999998",
        password_hash="hash",
        role_type="canteen_staff",
        is_active=True,
        is_email_validated=True,
    )
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina QA", location="Bloco C",
        is_open=True, opening_hours=opening_hours or [], moderation_status="approved",
    )
    product = ProductModel(
        id=uuid4(), canteen_id=canteen.id, name="Coxinha QA", description=None,
        price="7.50", is_fast_stock_enabled=False, is_active=product_active,
    )
    zone = DropOffZoneModel(id=uuid4(), name="Bloco C", description=None, capacity_total=10, is_active=True)
    db_session.add_all([staff, canteen, product, zone])
    db_session.commit()
    return str(canteen.id), str(product.id), str(zone.id)


def _payload(canteen_id: str, product_id: str, zone_id: str, customer_id: str = str(AUTH_USER_ID)) -> dict:
    return {
        "customer_id": customer_id,
        "canteen_id": canteen_id,
        "drop_off_zone_id": zone_id,
        "location_details": "Sala 42",
        "items": [{"product_id": product_id, "quantity": 2}],
    }


def test_create_order_uses_server_price_and_commits_items(db_session: Session, mock_current_user: User) -> None:
    canteen_id, product_id, zone_id = _catalog(db_session)

    response = create_order(OrderCreate(**_payload(canteen_id, product_id, zone_id)), db_session, mock_current_user)

    assert str(response.customer_id) == str(AUTH_USER_ID)
    assert response.location_details == "Sala 42"
    assert response.total_amount == 15
    assert response.items[0].unit_price == 7.5
    order_id = UUID(response.id).hex
    assert db_session.execute(text("SELECT count(*) FROM orders WHERE id = :id"), {"id": order_id}).scalar_one() == 1
    assert db_session.execute(text("SELECT count(*) FROM order_items WHERE order_id = :id"), {"id": order_id}).scalar_one() == 1
    assert db_session.execute(text("SELECT location_details FROM orders WHERE id = :id"), {"id": order_id}).scalar_one() == "Sala 42"


def test_create_order_rejects_customer_impersonation(db_session: Session, mock_current_user: User) -> None:
    canteen_id, product_id, zone_id = _catalog(db_session)
    orders_before = db_session.query(OrderModel).count()

    with pytest.raises(HTTPException) as error:
        create_order(OrderCreate(**_payload(canteen_id, product_id, zone_id, str(uuid4()))), db_session, mock_current_user)

    assert error.value.status_code == 403
    assert db_session.query(OrderModel).count() == orders_before


def test_create_order_rejects_client_price_and_unavailable_product(
    db_session: Session,
    mock_current_user: User,
) -> None:
    canteen_id, product_id, zone_id = _catalog(db_session, product_active=False)
    payload = _payload(canteen_id, product_id, zone_id)
    payload["items"][0]["unit_price"] = "0.01"

    with pytest.raises(ValidationError):
        OrderCreate(**payload)

    payload["items"][0].pop("unit_price")
    with pytest.raises(HTTPException) as error:
        create_order(OrderCreate(**payload), db_session, mock_current_user)
    assert error.value.status_code == 409


def test_create_order_rejects_canteen_outside_business_hours(
    db_session: Session,
    mock_current_user: User,
) -> None:
    closed_schedule = [
        {"day": day, "opens_at": "08:00", "closes_at": "18:00", "is_open": False}
        for day in ("weekdays", "saturday", "sunday")
    ]
    canteen_id, product_id, zone_id = _catalog(db_session, opening_hours=closed_schedule)

    with pytest.raises(HTTPException) as error:
        create_order(
            OrderCreate(**_payload(canteen_id, product_id, zone_id)),
            db_session,
            mock_current_user,
        )

    assert error.value.status_code == 409

"""Regression tests for the backend security audit."""

from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import CanteenModel, OrderItemModel, OrderModel, ProductModel, UserModel
from app.dependencies.auth import get_current_user
from main import app


def _user(role: str, name: str) -> UserModel:
    return UserModel(
        id=uuid4(),
        name=name,
        email=f"{uuid4()}@ufca.edu.br",
        whatsapp="5588999999999",
        password_hash="hash",
        role_type=role,
        is_active=True,
        is_email_validated=True,
    )


def test_customer_cannot_read_another_customers_order(
    client: TestClient, db_session: Session
) -> None:
    owner = _user("customer", "Owner")
    attacker = _user("customer", "Attacker")
    staff = _user("canteen_staff", "Staff")
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina", location="Bloco A", is_open=True
    )
    order = OrderModel(
        id=uuid4(), customer_id=owner.id, canteen_id=canteen.id,
        fulfillment_type="pickup", status="ready_for_pickup", total_amount="8.00",
        pickup_pin="4821",
    )
    db_session.add_all([owner, attacker, staff, canteen, order])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: attacker

    response = client.get(f"/orders/{order.id}")

    assert response.status_code == 403
    assert "4821" not in response.text


def test_canteen_staff_cannot_create_customer_order(
    client: TestClient, db_session: Session
) -> None:
    staff = _user("canteen_staff", "Staff")
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina", location="Bloco A", is_open=True
    )
    product = ProductModel(
        id=uuid4(), canteen_id=canteen.id, name="Produto", price="8.00",
        is_active=True, is_fast_stock_enabled=False,
    )
    db_session.add_all([staff, canteen, product])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: staff

    response = client.post(
        "/orders/",
        json={
            "customer_id": str(staff.id), "canteen_id": str(canteen.id),
            "fulfillment_type": "pickup", "items": [
                {"product_id": str(product.id), "quantity": 1}
            ],
        },
    )

    assert response.status_code == 403


def test_created_order_returns_persisted_item_identifier(
    client: TestClient, db_session: Session
) -> None:
    customer = _user("customer", "Customer")
    staff = _user("canteen_staff", "Staff")
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina", location="Bloco A", is_open=True
    )
    product = ProductModel(
        id=uuid4(), canteen_id=canteen.id, name="Produto", price="8.00",
        is_active=True, is_fast_stock_enabled=False,
    )
    db_session.add_all([customer, staff, canteen, product])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: customer

    response = client.post(
        "/orders/",
        json={
            "customer_id": str(customer.id), "canteen_id": str(canteen.id),
            "fulfillment_type": "pickup", "items": [
                {"product_id": str(product.id), "quantity": 1}
            ],
        },
    )

    assert response.status_code == 201
    persisted_item = db_session.query(OrderItemModel).filter_by(
        order_id=UUID(response.json()["id"])
    ).one()
    assert response.json()["items"][0]["id"] == str(persisted_item.id)

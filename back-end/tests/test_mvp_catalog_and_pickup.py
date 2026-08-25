from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import CanteenModel, ProductModel, UserModel
from app.dependencies.auth import get_current_user
from main import app


def _user(role: str, name: str) -> UserModel:
    return UserModel(id=uuid4(), name=name, email=f"{uuid4()}@example.com", whatsapp="5588999999999", password_hash="hash", role_type=role, is_active=True, is_email_validated=True)


def test_seller_product_crud_is_scoped_to_owned_canteen(client: TestClient, db_session: Session) -> None:
    staff_a, staff_b = _user("canteen_staff", "Staff A"), _user("canteen_staff", "Staff B")
    canteen_a = CanteenModel(id=uuid4(), user_id=staff_a.id, name="Cantina A", location="A", is_open=True)
    canteen_b = CanteenModel(id=uuid4(), user_id=staff_b.id, name="Cantina B", location="B", is_open=True)
    foreign = ProductModel(id=uuid4(), canteen_id=canteen_b.id, name="Foreign", price="5.00", is_active=True, is_fast_stock_enabled=False)
    db_session.add_all([staff_a, staff_b, canteen_a, canteen_b, foreign])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: staff_a

    created = client.post("/canteens/me/products", json={"name": "Coxinha", "description": "Quente", "price": "7.50", "image_url": "https://img.example/coxinha.jpg", "is_active": True})
    assert created.status_code == 201
    assert created.json()["canteen_id"] == str(canteen_a.id)
    assert client.patch(f"/canteens/me/products/{foreign.id}", json={"is_active": False}).status_code == 404
    assert {item["name"] for item in client.get("/canteens/me/products").json()} == {"Coxinha"}


def test_seller_can_persist_business_hours(client: TestClient, db_session: Session) -> None:
    staff = _user("canteen_staff", "Staff")
    canteen = CanteenModel(id=uuid4(), user_id=staff.id, name="Cantina", location="Bloco H", is_open=True)
    db_session.add_all([staff, canteen])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: staff
    hours = [{"day": "weekdays", "opens_at": "08:00", "closes_at": "18:00", "is_open": True}]
    response = client.patch("/canteens/me", json={"opening_hours": hours})
    assert response.status_code == 200
    assert response.json()["opening_hours"] == hours


def test_pickup_order_needs_no_drop_off_zone_and_is_visible_only_to_customer(client: TestClient, db_session: Session) -> None:
    customer, other, staff = _user("customer", "Customer"), _user("customer", "Other"), _user("canteen_staff", "Staff")
    canteen = CanteenModel(id=uuid4(), user_id=staff.id, name="Cantina", location="Bloco H", is_open=True)
    product = ProductModel(id=uuid4(), canteen_id=canteen.id, name="Coxinha", price="8.00", is_active=True, is_fast_stock_enabled=False)
    db_session.add_all([customer, other, staff, canteen, product])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: customer
    created = client.post("/orders/", json={"customer_id": str(customer.id), "canteen_id": str(canteen.id), "fulfillment_type": "pickup", "drop_off_zone_id": None, "items": [{"product_id": str(product.id), "quantity": 2}]})
    assert created.status_code == 201
    assert created.json()["fulfillment_type"] == "pickup"
    own = client.get("/orders/me")
    assert own.status_code == 200 and [entry["id"] for entry in own.json()] == [created.json()["id"]]
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.get("/orders/me").json() == []


def test_non_customer_is_rejected_before_creating_delivery_order(client: TestClient, db_session: Session) -> None:
    response = client.post("/orders/", json={"customer_id": str(uuid4()), "canteen_id": str(uuid4()), "fulfillment_type": "delivery", "items": [{"product_id": str(uuid4()), "quantity": 1}]})
    assert response.status_code == 403

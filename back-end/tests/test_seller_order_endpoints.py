from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import CanteenModel, DropOffZoneModel, OrderItemModel, OrderModel, ProductModel, UserModel
from app.dependencies.auth import get_current_user
from main import app


def _user(role: str, label: str) -> UserModel:
    return UserModel(
        id=uuid4(), name=label,
        email=f"{label.lower().replace(' ', '-')}-{uuid4()}@example.com",
        whatsapp="5588999999999", password_hash="hash", role_type=role,
        is_active=True, is_email_validated=True,
    )


def _seller_catalog(db: Session):
    staff_a = _user("canteen_staff", "Staff A")
    staff_b = _user("canteen_staff", "Staff B")
    customer = _user("customer", "Customer QA")
    canteen_a = CanteenModel(id=uuid4(), user_id=staff_a.id, name="Cantina A", location="Bloco A", is_open=True)
    canteen_b = CanteenModel(id=uuid4(), user_id=staff_b.id, name="Cantina B", location="Bloco B", is_open=True)
    product_a = ProductModel(id=uuid4(), canteen_id=canteen_a.id, name="Coxinha", description=None, price="8.00", is_fast_stock_enabled=False, is_active=True)
    product_b = ProductModel(id=uuid4(), canteen_id=canteen_b.id, name="Pastel", description=None, price="9.00", is_fast_stock_enabled=False, is_active=True)
    zone = DropOffZoneModel(id=uuid4(), name="Biblioteca", description="Entrada principal", capacity_total=20, is_active=True)
    order_a = OrderModel(id=uuid4(), customer_id=customer.id, canteen_id=canteen_a.id, drop_off_zone_id=zone.id, location_details="Sala 12", status="paid", total_amount="16.00")
    order_b = OrderModel(id=uuid4(), customer_id=customer.id, canteen_id=canteen_b.id, drop_off_zone_id=zone.id, location_details="Laboratório 3", status="paid", total_amount="9.00")
    item_a = OrderItemModel(id=uuid4(), order_id=order_a.id, product_id=product_a.id, unit_price="8.00", quantity=2)
    item_b = OrderItemModel(id=uuid4(), order_id=order_b.id, product_id=product_b.id, unit_price="9.00", quantity=1)
    db.add_all([staff_a, staff_b, customer, canteen_a, canteen_b, product_a, product_b, zone, order_a, order_b, item_a, item_b])
    db.commit()
    return staff_a, staff_b, order_a, order_b


def test_seller_orders_are_isolated_by_authenticated_canteen(client: TestClient, db_session: Session) -> None:
    staff_a, _, order_a, order_b = _seller_catalog(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff_a

    response = client.get("/canteens/me/orders")

    assert response.status_code == 200
    payload = response.json()
    assert [entry["id"] for entry in payload] == [str(order_a.id)]
    assert str(order_b.id) not in {entry["id"] for entry in payload}
    assert payload[0]["customer"] == {"id": str(order_a.customer_id), "name": "Customer QA"}
    assert payload[0]["destination"]["name"] == "Biblioteca"
    assert payload[0]["location_details"] == "Sala 12"
    assert payload[0]["items"][0]["name"] == "Coxinha"
    assert payload[0]["total_amount"] == "16.00"


def test_seller_history_contains_only_completed_orders_from_authenticated_canteen(client: TestClient, db_session: Session) -> None:
    staff_a, _, order_a, order_b = _seller_catalog(db_session)
    completed_a = OrderModel(
        id=uuid4(), customer_id=order_a.customer_id, canteen_id=order_a.canteen_id,
        drop_off_zone_id=order_a.drop_off_zone_id, status="completed", total_amount="8.00",
    )
    completed_b = OrderModel(
        id=uuid4(), customer_id=order_b.customer_id, canteen_id=order_b.canteen_id,
        drop_off_zone_id=order_b.drop_off_zone_id, status="completed", total_amount="9.00",
    )
    db_session.add_all([completed_a, completed_b])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: staff_a

    response = client.get("/canteens/me/orders/history")

    assert response.status_code == 200
    assert [entry["id"] for entry in response.json()] == [str(completed_a.id)]
    assert response.json()[0]["status"] == "completed"


def test_seller_cannot_read_or_update_another_canteen_order(client: TestClient, db_session: Session) -> None:
    staff_a, _, _, order_b = _seller_catalog(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff_a

    response = client.patch(f"/canteens/me/orders/{order_b.id}/status", json={"status": "preparing"})

    assert response.status_code == 404
    db_session.refresh(order_b)
    assert order_b.status == "paid"


def test_seller_order_status_machine_commits_only_valid_transitions(client: TestClient, db_session: Session) -> None:
    staff_a, _, order_a, _ = _seller_catalog(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff_a

    preparing = client.patch(f"/canteens/me/orders/{order_a.id}/status", json={"status": "preparing"})
    assert preparing.status_code == 200
    assert preparing.json()["status"] == "preparing"

    ready = client.patch(f"/canteens/me/orders/{order_a.id}/status", json={"status": "ready_for_pickup"})
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready_for_pickup"
    db_session.refresh(order_a)
    assert order_a.status == "ready_for_pickup"

    regression = client.patch(f"/canteens/me/orders/{order_a.id}/status", json={"status": "preparing"})
    assert regression.status_code == 409


def test_seller_order_status_machine_rejects_skipped_transition(client: TestClient, db_session: Session) -> None:
    staff_a, _, order_a, _ = _seller_catalog(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff_a

    skipped = client.patch(f"/canteens/me/orders/{order_a.id}/status", json={"status": "ready_for_pickup"})

    assert skipped.status_code == 409
    assert "Cannot move order" in skipped.json()["detail"]


def test_seller_endpoints_require_authentication_and_staff_role(client: TestClient, db_session: Session) -> None:
    _seller_catalog(db_session)
    app.dependency_overrides.pop(get_current_user, None)
    assert client.get("/canteens/me/orders").status_code == 401

    customer = _user("customer", "Unauthorized Customer")
    db_session.add(customer)
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: customer
    assert client.get("/canteens/me/orders").status_code == 403


def _ready_pickup(db: Session):
    staff_a, staff_b, order_a, _ = _seller_catalog(db)
    order_a.fulfillment_type = "pickup"
    order_a.drop_off_zone_id = None
    order_a.status = "ready_for_pickup"
    order_a.pickup_pin = "4821"
    db.commit()
    return staff_a, staff_b, order_a


def test_owner_completes_pickup_with_valid_pin_and_repeat_is_idempotent(client: TestClient, db_session: Session) -> None:
    staff, _, order = _ready_pickup(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff
    url = f"/canteens/me/orders/{order.id}/pickup/confirm"

    first = client.post(url, json={"pickup_pin": "4821"})
    repeated = client.post(url, json={"pickup_pin": "4821"})

    assert first.status_code == 200 and first.json()["status"] == "completed"
    assert repeated.status_code == 200 and repeated.json() == first.json()
    db_session.refresh(order)
    assert order.status == "completed"


def test_pickup_confirmation_rejects_invalid_pin(client: TestClient, db_session: Session) -> None:
    staff, _, order = _ready_pickup(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff
    url = f"/canteens/me/orders/{order.id}/pickup/confirm"

    invalid = client.post(url, json={"pickup_pin": "0000"})
    assert invalid.status_code == 409
    db_session.refresh(order)
    assert order.status == "ready_for_pickup"


def test_pickup_confirmation_rejects_wrong_status(client: TestClient, db_session: Session) -> None:
    staff, _, order = _ready_pickup(db_session)
    app.dependency_overrides[get_current_user] = lambda: staff
    url = f"/canteens/me/orders/{order.id}/pickup/confirm"
    order.status = "preparing"
    db_session.commit()
    wrong_status = client.post(url, json={"pickup_pin": "4821"})
    assert wrong_status.status_code == 409
    assert "not ready" in wrong_status.json()["detail"]


def test_pickup_confirmation_hides_other_canteen_order(client: TestClient, db_session: Session) -> None:
    _, other_staff, order = _ready_pickup(db_session)
    app.dependency_overrides[get_current_user] = lambda: other_staff

    response = client.post(f"/canteens/me/orders/{order.id}/pickup/confirm", json={"pickup_pin": "4821"})

    assert response.status_code == 404
    db_session.refresh(order)
    assert order.status == "ready_for_pickup"

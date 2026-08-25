from __future__ import annotations

from http import HTTPStatus
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import CanteenModel


def test_canteen_create_get_patch_contract_and_commit(
    client: TestClient,
    db_session: Session,
) -> None:
    owner_id = str(uuid4())
    create_response = client.post(
        "/canteens/",
        json={
            "user_id": owner_id,
            "name": "  Cantina Central  ",
            "location": "  Campus Juazeiro  ",
            "is_open": True,
        },
    )

    assert create_response.status_code == HTTPStatus.CREATED
    created = create_response.json()
    assert set(created) == {"id", "user_id", "name", "location", "is_open", "products", "opening_hours"}
    assert created["name"] == "Cantina Central"
    assert created["location"] == "Campus Juazeiro"

    db_session.expire_all()
    persisted = db_session.get(CanteenModel, UUID(created["id"]))
    assert persisted is not None
    assert persisted.name == "Cantina Central"
    assert persisted.location == "Campus Juazeiro"

    patch_response = client.patch(
        f"/canteens/{created['id']}",
        json={"name": "Cantina do Bloco B", "location": "Bloco B", "is_open": False},
    )
    assert patch_response.status_code == HTTPStatus.OK
    assert patch_response.json()["name"] == "Cantina do Bloco B"
    assert patch_response.json()["location"] == "Bloco B"
    assert patch_response.json()["is_open"] is False

    get_response = client.get(f"/canteens/{created['id']}")
    assert get_response.status_code == HTTPStatus.OK
    assert get_response.json() == patch_response.json()


def test_canteen_list_returns_persisted_identity(client: TestClient, db_session: Session) -> None:
    owner_id = str(uuid4())
    response = client.post(
        "/canteens/",
        json={
            "user_id": owner_id,
            "name": "Marmitas da Tia Cleide",
            "location": "Biblioteca Central",
        },
    )
    assert response.status_code == HTTPStatus.CREATED

    listed = client.get("/canteens/")
    assert listed.status_code == HTTPStatus.OK
    assert any(
        canteen["name"] == "Marmitas da Tia Cleide"
        and canteen["location"] == "Biblioteca Central"
        for canteen in listed.json()
    )


def test_canteen_contract_rejects_blank_name_and_location(client: TestClient) -> None:
    response = client.post(
        "/canteens/",
        json={"user_id": str(uuid4()), "name": "  ", "location": "  "},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_canteen_contract_rejects_unknown_write_fields(client: TestClient) -> None:
    response = client.post(
        "/canteens/",
        json={
            "user_id": str(uuid4()),
            "name": "Cantina válida",
            "location": "Local válido",
            "products": [str(uuid4())],
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_canteen_get_and_patch_return_not_found(client: TestClient) -> None:
    missing_id = uuid4()
    assert client.get(f"/canteens/{missing_id}").status_code == HTTPStatus.NOT_FOUND
    assert client.patch(f"/canteens/{missing_id}", json={"name": "Valid Name"}).status_code == HTTPStatus.NOT_FOUND

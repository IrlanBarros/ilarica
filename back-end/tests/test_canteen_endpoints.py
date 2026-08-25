from __future__ import annotations

from http import HTTPStatus
from datetime import datetime, timezone
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
    assert set(created) == {
        "id", "user_id", "name", "location", "is_open", "products", "opening_hours",
        "is_accepting_orders", "next_opening_at",
        "description", "logo_url", "commercial_terms_accepted_at", "moderation_status",
        "moderation_reviewed_at", "rejection_reason",
    }
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

    persisted.description = "Uma cantina completa para a comunidade acadêmica."
    persisted.logo_url = "https://images.example/cantina.png"
    persisted.commercial_terms_accepted_at = datetime.now(timezone.utc)
    persisted.moderation_status = "approved"
    db_session.commit()

    get_response = client.get(f"/canteens/{created['id']}")
    assert get_response.status_code == HTTPStatus.OK
    assert get_response.json()["name"] == patch_response.json()["name"]
    assert get_response.json()["moderation_status"] == "approved"


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

    created = response.json()
    persisted = db_session.get(CanteenModel, UUID(created["id"]))
    assert persisted is not None
    persisted.moderation_status = "approved"
    db_session.commit()

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

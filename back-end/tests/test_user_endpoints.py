"""Integration tests for User endpoints using TestClient and in-memory SQLite."""

from __future__ import annotations

from http import HTTPStatus
from uuid import uuid4

from fastapi.testclient import TestClient

from app.database.session import get_db
from main import app


def test_create_user_success(client: TestClient):
    payload = {"name": "Test User", "email": "testuser@ufca.edu.br", "password": "Secret123", "role": "customer"}
    resp = client.post("/users/", json=payload)
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["role"] == payload["role"]


def test_create_user_validation_error(client: TestClient):
    # missing email
    payload = {"name": "No Email", "password": "Secret123", "role": "customer"}
    resp = client.post("/users/", json=payload)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user_is_public_without_auth_override(client: TestClient):
    db_override = app.dependency_overrides[get_db]
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = db_override

    payload = {"name": "Public User", "email": "public@ufca.edu.br", "password": "Secret123", "role": "customer"}
    resp = client.post("/users/", json=payload)

    assert resp.status_code == HTTPStatus.CREATED


def test_list_users(client: TestClient):
    # ensure at least one user exists from previous test
    resp = client.get("/users/")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert isinstance(data, list)


def test_get_user_not_found(client: TestClient):
    resp = client.get(f"/users/{uuid4()}")
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_get_user_by_id(client: TestClient):
    # create a user then fetch by id
    payload = {"name": "Fetch User", "email": "fetch@ufca.edu.br", "password": "Secret123", "role": "customer"}
    create = client.post("/users/", json=payload)
    assert create.status_code == HTTPStatus.CREATED
    user = create.json()

    resp = client.get(f"/users/{user['id']}")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["email"] == payload["email"]


def test_get_current_user_profile(client: TestClient):
    resp = client.get("/users/me")

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["id"] == "test-auth-user"
    assert data["email"] == "qa-auth@ufca.edu.br"
    assert data["role"] == "admin"
    assert "password" not in data


def test_update_user_patch(client: TestClient):
    payload = {"name": "Patch User", "email": "patch@ufca.edu.br", "password": "Secret123", "role": "customer"}
    create = client.post("/users/", json=payload)
    assert create.status_code == HTTPStatus.CREATED
    user = create.json()

    patch = {"name": "Patched Name"}
    resp = client.patch(f"/users/{user['id']}", json=patch)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["name"] == "Patched Name"


def test_delete_user(client: TestClient):
    payload = {"name": "Delete User", "email": "delete@ufca.edu.br", "password": "Secret123", "role": "customer"}
    create = client.post("/users/", json=payload)
    assert create.status_code == HTTPStatus.CREATED
    user = create.json()

    resp = client.delete(f"/users/{user['id']}")
    assert resp.status_code == HTTPStatus.OK
    # confirm deletion
    get = client.get(f"/users/{user['id']}")
    assert get.status_code == HTTPStatus.NOT_FOUND

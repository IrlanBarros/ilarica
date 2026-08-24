"""Authentication and authorization integration tests."""

from __future__ import annotations

from http import HTTPStatus
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database.models import UserModel
from app.database.session import get_db
from tests.conftest import override_get_db
from main import app


def test_login_success_returns_token(client: TestClient, db_session: Session):
    """Should return access token when credentials are valid."""
    user = UserModel(
        id=uuid4(),
        name="Auth User",
        email="auth.success@ufca.edu.br",
        whatsapp="5588999999999",
        password_hash=get_password_hash("Secret123"),
        role_type="customer",
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "auth.success@ufca.edu.br", "password": "Secret123"},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_unregistered_email_returns_401(client: TestClient):
    """Should reject login with unknown user."""
    response = client.post(
        "/auth/login",
        data={"username": "missing@ufca.edu.br", "password": "Secret123"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_login_with_wrong_password_returns_401(client: TestClient, db_session: Session):
    """Should reject login when password is invalid."""
    user = UserModel(
        id=uuid4(),
        name="Invalid Password User",
        email="auth.wrongpass@ufca.edu.br",
        whatsapp="5588999999998",
        password_hash=get_password_hash("Secret123"),
        role_type="customer",
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "auth.wrongpass@ufca.edu.br", "password": "Wrong123"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_protected_route_without_override_returns_401(client: TestClient):
    """When auth override is removed, protected routes must return 401."""
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/users/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.headers.get("WWW-Authenticate") == "Bearer"

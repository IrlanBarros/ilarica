from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.database.models import UserModel
from app.dependencies.auth import get_current_user
from main import app


def _customer() -> UserModel:
    return UserModel(
        id=uuid4(), name="Customer Security", email=f"security-{uuid4()}@aluno.ufca.edu.br",
        whatsapp="5588999999999", password_hash="hash", role_type="customer",
        is_active=True, is_email_validated=True,
    )


def test_legacy_generic_mutations_reject_non_admin_users(client: TestClient) -> None:
    app.dependency_overrides[get_current_user] = _customer
    resource_id = uuid4()

    responses = [
        client.patch(f"/orders/{resource_id}", json={"status": "completed"}),
        client.delete(f"/orders/{resource_id}"),
        client.patch(f"/canteens/{resource_id}", json={"name": "Unauthorized"}),
        client.delete(f"/canteens/{resource_id}"),
        client.patch(f"/products/{resource_id}", json={"name": "Unauthorized"}),
        client.delete(f"/products/{resource_id}"),
        client.patch(f"/users/{resource_id}", json={"name": "Unauthorized"}),
        client.delete(f"/users/{resource_id}"),
    ]

    assert all(response.status_code == 403 for response in responses)


def test_legacy_generic_mutations_require_authentication(client: TestClient) -> None:
    app.dependency_overrides.pop(get_current_user, None)
    response = client.delete(f"/orders/{uuid4()}")
    assert response.status_code == 401

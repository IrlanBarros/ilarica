from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from main import app


def test_payment_endpoint_rejects_client_controlled_amount(client: TestClient) -> None:
    response = client.post(
        "/payment-transactions/",
        json={
            "order_id": "00000000-0000-0000-0000-000000000010",
            "payment_method": "pix",
            "amount": "0.01",
        },
        headers={"Idempotency-Key": "endpoint-idempotency-0001"},
    )
    assert response.status_code == 422


def test_payment_endpoint_requires_authentication(client: TestClient) -> None:
    def unauthorized():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_user] = unauthorized
    response = client.post(
        "/payment-transactions/",
        json={
            "order_id": "00000000-0000-0000-0000-000000000010",
            "payment_method": "pix",
        },
        headers={"Idempotency-Key": "endpoint-idempotency-0002"},
    )
    assert response.status_code == 401

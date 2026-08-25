from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import CanteenModel, UserModel
from app.dependencies.auth import get_current_user
from main import app


def _user(role: str, label: str) -> UserModel:
    return UserModel(
        id=uuid4(), name=label, email=f"{uuid4()}@ufca.edu.br",
        whatsapp="5588999999999", password_hash="hash", role_type=role,
        is_active=True, is_email_validated=True,
    )


def test_staff_onboarding_records_server_timestamp_and_admin_approval_controls_publication(
    client: TestClient,
    db_session: Session,
) -> None:
    staff = _user("canteen_staff", "Seller")
    admin = _user("admin", "Admin")
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina Nova", location="Bloco C",
        is_open=True, moderation_status="pending",
    )
    db_session.add_all([staff, admin, canteen])
    db_session.commit()

    assert str(canteen.id) not in {item["id"] for item in client.get("/canteens/").json()}
    assert client.get(f"/canteens/{canteen.id}").status_code == 404

    app.dependency_overrides[get_current_user] = lambda: staff
    before = datetime.now(timezone.utc)
    onboarding = client.post(
        "/canteens/me/onboarding",
        json={
            "description": "Lanches artesanais preparados diariamente no campus.",
            "logo_url": "https://images.example/cantina.png",
            "accepted_commercial_terms": True,
        },
    )
    assert onboarding.status_code == 200
    accepted_at = datetime.fromisoformat(onboarding.json()["commercial_terms_accepted_at"])
    if accepted_at.tzinfo is None:
        accepted_at = accepted_at.replace(tzinfo=timezone.utc)
    assert accepted_at >= before
    assert onboarding.json()["moderation_status"] == "pending"

    app.dependency_overrides[get_current_user] = lambda: admin
    pending = client.get("/canteens/moderation", params={"moderation_status": "pending"})
    assert pending.status_code == 200
    assert str(canteen.id) in {item["id"] for item in pending.json()}
    approved = client.patch(
        f"/canteens/{canteen.id}/moderation", json={"status": "approved"}
    )
    assert approved.status_code == 200
    assert approved.json()["moderation_status"] == "approved"

    assert str(canteen.id) in {item["id"] for item in client.get("/canteens/").json()}
    assert client.get(f"/canteens/{canteen.id}").status_code == 200


def test_rejection_requires_reason_hides_canteen_and_allows_resubmission(
    client: TestClient,
    db_session: Session,
) -> None:
    staff = _user("canteen_staff", "Seller Rejected")
    admin = _user("admin", "Admin Review")
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina Revisão", location="Bloco D",
        description="Descrição comercial completa para avaliação.",
        logo_url="https://images.example/logo.png", is_open=True,
        commercial_terms_accepted_at=datetime.now(timezone.utc), moderation_status="pending",
    )
    db_session.add_all([staff, admin, canteen])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: admin

    invalid = client.patch(f"/canteens/{canteen.id}/moderation", json={"status": "rejected"})
    assert invalid.status_code == 422
    rejected = client.patch(
        f"/canteens/{canteen.id}/moderation",
        json={"status": "rejected", "rejection_reason": "Envie uma logo com melhor resolução."},
    )
    assert rejected.status_code == 200
    assert rejected.json()["moderation_status"] == "rejected"
    assert rejected.json()["is_open"] is False
    assert client.get(f"/canteens/{canteen.id}").status_code == 404

    app.dependency_overrides[get_current_user] = lambda: staff
    resubmitted = client.post(
        "/canteens/me/onboarding",
        json={
            "description": "Descrição comercial revisada e pronta para nova avaliação.",
            "logo_url": "https://images.example/logo-hd.png",
            "accepted_commercial_terms": True,
        },
    )
    assert resubmitted.status_code == 200
    assert resubmitted.json()["moderation_status"] == "pending"
    assert resubmitted.json()["rejection_reason"] is None


def test_non_admin_cannot_moderate_canteens(
    client: TestClient,
    db_session: Session,
) -> None:
    staff = _user("canteen_staff", "Unauthorized Seller")
    canteen = CanteenModel(
        id=uuid4(), user_id=staff.id, name="Cantina", location="Bloco A",
        moderation_status="pending",
    )
    db_session.add_all([staff, canteen])
    db_session.commit()
    app.dependency_overrides[get_current_user] = lambda: staff

    assert client.get("/canteens/moderation").status_code == 403
    assert client.patch(
        f"/canteens/{canteen.id}/moderation", json={"status": "approved"}
    ).status_code == 403

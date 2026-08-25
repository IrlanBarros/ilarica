from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import UserModel
from app.domain.catalog.canteen import Canteen
from app.repositories.sqlalchemy_repositories import SQLAlchemyCanteenRepository


def test_canteen_repository_round_trip_persists_required_fields(db_session: Session) -> None:
    owner_id = uuid4()
    db_session.add(
        UserModel(
            id=owner_id,
            name="Owner Repository",
            email=f"owner-{owner_id}@example.com",
            whatsapp="5588999999901",
            password_hash="hashed",
            role_type="canteen_staff",
            is_email_validated=True,
        )
    )
    repository = SQLAlchemyCanteenRepository(db_session)
    canteen_id = str(uuid4())

    repository.add(
        Canteen(
            id=canteen_id,
            user_id=str(owner_id),
            name="Cantina Persistida",
            location="Bloco de Testes",
            is_open=True,
        )
    )
    db_session.commit()
    db_session.expire_all()

    persisted = repository.get_by_id(canteen_id)
    assert persisted is not None
    assert persisted.name == "Cantina Persistida"
    assert persisted.location == "Bloco de Testes"
    assert persisted.is_open is True

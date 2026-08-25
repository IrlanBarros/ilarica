from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.database.models import PasswordResetTokenModel, UserModel
from app.services.password_reset_service import InvalidPasswordResetTokenError, PasswordResetService


def test_password_reset_is_single_use_and_stores_only_digest(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    user = UserModel(id=uuid4(), name="Cliente", email="reset@ufca.edu.br", whatsapp="5588999999999", password_hash="old", role_type="customer", is_active=True, is_email_validated=True)
    db_session.add(user)
    db_session.commit()
    captured: list[str] = []
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setattr(PasswordResetService, "_send_email", staticmethod(lambda _recipient, token: captured.append(token)))

    service = PasswordResetService(db_session)
    service.request(user.email)

    assert len(captured) == 1
    persisted = db_session.query(PasswordResetTokenModel).one()
    assert captured[0] not in persisted.token_hash
    service.confirm(captured[0], "NewPassword123")
    db_session.refresh(user)
    assert verify_password("NewPassword123", user.password_hash)
    with pytest.raises(InvalidPasswordResetTokenError):
        service.confirm(captured[0], "AnotherPassword123")


def test_password_reset_request_does_not_reveal_unknown_email(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[str] = []
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setattr(PasswordResetService, "_send_email", staticmethod(lambda _recipient, token: sent.append(token)))
    PasswordResetService(db_session).request("unknown@ufca.edu.br")
    assert sent == []

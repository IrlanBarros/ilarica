from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.database.models import EmailVerificationTokenModel, UserModel
from app.services.email_verification_service import (
    EmailVerificationService,
    InvalidEmailVerificationTokenError,
)


def _pending_user(db_session: Session) -> UserModel:
    user = UserModel(
        id=uuid4(), name="Cliente Pendente", email=f"pending-{uuid4()}@ufca.edu.br",
        whatsapp="5588999999999", password_hash="hash", role_type="customer",
        is_active=True, is_email_validated=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_verification_is_hashed_single_use_and_activates_email(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _pending_user(db_session)
    captured: list[str] = []
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setattr(
        EmailVerificationService,
        "_send_email",
        staticmethod(lambda _recipient, token: captured.append(token)),
    )

    service = EmailVerificationService(db_session)
    assert service.request(user.email)
    persisted = db_session.query(EmailVerificationTokenModel).filter_by(user_id=user.id).one()
    assert captured[0] not in persisted.token_hash

    service.confirm(captured[0])
    db_session.refresh(user)
    assert user.is_email_validated is True
    with pytest.raises(InvalidEmailVerificationTokenError):
        service.confirm(captured[0])


def test_expired_verification_token_is_rejected(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = _pending_user(db_session)
    captured: list[str] = []
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setattr(
        EmailVerificationService,
        "_send_email",
        staticmethod(lambda _recipient, token: captured.append(token)),
    )
    service = EmailVerificationService(db_session)
    service.request(user.email)
    token = db_session.query(EmailVerificationTokenModel).filter_by(user_id=user.id).one()
    token.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    with pytest.raises(InvalidEmailVerificationTokenError):
        service.confirm(captured[0])


def test_request_does_not_reveal_unknown_or_already_verified_email(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent: list[str] = []
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setattr(
        EmailVerificationService,
        "_send_email",
        staticmethod(lambda _recipient, token: sent.append(token)),
    )
    assert not EmailVerificationService(db_session).request("unknown@ufca.edu.br")
    assert sent == []

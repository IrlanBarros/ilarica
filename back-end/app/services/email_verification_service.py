"""Secure, expiring and single-use institutional email verification."""

from __future__ import annotations

import hashlib
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.database.models import EmailVerificationTokenModel, UserModel


class EmailVerificationUnavailableError(RuntimeError):
    pass


class InvalidEmailVerificationTokenError(ValueError):
    pass


class EmailVerificationService:
    EXPIRATION_MINUTES = 15

    def __init__(self, db: Session) -> None:
        self.db = db

    def request(self, email: str, *, skip_if_unconfigured: bool = False) -> bool:
        if not os.getenv("SMTP_HOST"):
            if skip_if_unconfigured:
                return False
            raise EmailVerificationUnavailableError("Email verification is not configured")
        user = self.db.query(UserModel).filter(
            UserModel.email == email,
            UserModel.is_active.is_(True),
            UserModel.is_email_validated.is_(False),
        ).one_or_none()
        if user is None:
            return False

        raw_token = secrets.token_urlsafe(48)
        now = datetime.now(timezone.utc)
        self.db.query(EmailVerificationTokenModel).filter(
            EmailVerificationTokenModel.user_id == user.id,
            EmailVerificationTokenModel.used_at.is_(None),
        ).update({EmailVerificationTokenModel.used_at: now}, synchronize_session=False)
        self.db.add(EmailVerificationTokenModel(
            user_id=user.id,
            token_hash=self._digest(raw_token),
            expires_at=now + timedelta(minutes=self.EXPIRATION_MINUTES),
        ))
        try:
            self.db.flush()
            self._send_email(user.email, raw_token)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return True

    def confirm(self, raw_token: str) -> None:
        now = datetime.now(timezone.utc)
        token = self.db.query(EmailVerificationTokenModel).filter(
            EmailVerificationTokenModel.token_hash == self._digest(raw_token)
        ).with_for_update().one_or_none()
        expires_at = (
            token.expires_at.replace(tzinfo=timezone.utc)
            if token and token.expires_at.tzinfo is None
            else token.expires_at if token else None
        )
        if token is None or token.used_at is not None or expires_at is None or expires_at <= now:
            self.db.rollback()
            raise InvalidEmailVerificationTokenError("Invalid or expired email verification token")

        user = self.db.query(UserModel).filter(UserModel.id == token.user_id).with_for_update().one()
        if user.is_email_validated:
            self.db.rollback()
            raise InvalidEmailVerificationTokenError("Email is already verified")
        user.is_email_validated = True
        token.used_at = now
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _send_email(recipient: str, token: str) -> None:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
        message = EmailMessage()
        message["Subject"] = "Confirme seu e-mail — iLarica"
        message["From"] = os.environ["SMTP_FROM"]
        message["To"] = recipient
        message.set_content(
            "Confirme seu e-mail institucional pelo link abaixo em até 15 minutos:\n\n"
            f"{frontend_url}/verificar-email?token={quote(token)}\n\n"
            "O link funciona uma única vez. Se você não criou esta conta, ignore esta mensagem."
        )
        with smtplib.SMTP(
            os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "587")), timeout=10
        ) as server:
            if os.getenv("SMTP_STARTTLS", "true").lower() == "true":
                server.starttls()
            if os.getenv("SMTP_USER"):
                server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            server.send_message(message)

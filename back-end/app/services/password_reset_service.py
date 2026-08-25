"""Secure, single-use password recovery application service."""

from __future__ import annotations

import hashlib
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database.models import PasswordResetTokenModel, UserModel


class PasswordResetUnavailableError(RuntimeError):
    pass


class InvalidPasswordResetTokenError(ValueError):
    pass


class PasswordResetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def request(self, email: str) -> None:
        if not os.getenv("SMTP_HOST"):
            raise PasswordResetUnavailableError("Password recovery email is not configured")
        user = self.db.query(UserModel).filter(UserModel.email == email, UserModel.is_active.is_(True)).one_or_none()
        if user is None:
            return
        raw_token = secrets.token_urlsafe(48)
        now = datetime.now(timezone.utc)
        self.db.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.user_id == user.id,
            PasswordResetTokenModel.used_at.is_(None),
        ).update({PasswordResetTokenModel.used_at: now}, synchronize_session=False)
        self.db.add(PasswordResetTokenModel(
            user_id=user.id,
            token_hash=self._digest(raw_token),
            expires_at=now + timedelta(minutes=30),
        ))
        try:
            self.db.flush()
            self._send_email(user.email, raw_token)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def confirm(self, raw_token: str, new_password: str) -> None:
        now = datetime.now(timezone.utc)
        token = self.db.query(PasswordResetTokenModel).filter(
            PasswordResetTokenModel.token_hash == self._digest(raw_token)
        ).with_for_update().one_or_none()
        expires_at = token.expires_at.replace(tzinfo=timezone.utc) if token and token.expires_at.tzinfo is None else token.expires_at if token else None
        if token is None or token.used_at is not None or expires_at is None or expires_at <= now:
            self.db.rollback()
            raise InvalidPasswordResetTokenError("Invalid or expired password reset token")
        user = self.db.query(UserModel).filter(UserModel.id == token.user_id).with_for_update().one()
        user.password_hash = get_password_hash(new_password)
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
        message["Subject"] = "Redefinição de senha — iLarica"
        message["From"] = os.environ["SMTP_FROM"]
        message["To"] = recipient
        message.set_content(
            f"Use o link abaixo em até 30 minutos para redefinir sua senha:\n\n"
            f"{frontend_url}/redefinir-senha?token={quote(token)}\n\n"
            "Se você não solicitou a alteração, ignore esta mensagem."
        )
        with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "587")), timeout=10) as server:
            if os.getenv("SMTP_STARTTLS", "true").lower() == "true":
                server.starttls()
            if os.getenv("SMTP_USER"):
                server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            server.send_message(message)

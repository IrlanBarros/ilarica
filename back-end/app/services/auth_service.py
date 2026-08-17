"""Authentication service for login and token issuance."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.database.models import UserModel
from app.domain.access_identity.user import User


@dataclass
class AuthService:
    """Validate credentials and return a user/session token payload."""

    db: Session

    def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user_model = self.db.query(UserModel).filter(UserModel.email == email).one_or_none()
        if user_model is None:
            return None

        if not verify_password(password, user_model.password_hash):
            return None

        return User(
            id=str(user_model.id),
            email=user_model.email,
            password_hash=user_model.password_hash,
            role=user_model.role_type,
            is_active=True,
        )

    def login_for_access_token(self, email: str, password: str) -> str:
        """Authenticate and generate a JWT access token."""
        user = self.authenticate(email, password)
        if user is None:
            raise ValueError("Incorrect email or password")
        return create_access_token(subject=user.email)

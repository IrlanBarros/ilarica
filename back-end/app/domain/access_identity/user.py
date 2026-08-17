"""Access and identity user aggregate root."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from app.core.security import get_password_hash, verify_password
from app.domain.exceptions import InvalidCredentialsError, InvalidRoleError


@dataclass
class User:
    """Aggregate root for a platform user."""

    id: str
    email: str
    password_hash: str
    role: str = "customer"
    is_active: bool = True
    failed_login_attempts: int = 0
    last_login_at: str | None = None
    assigned_invitation_key: str | None = None

    VALID_ROLES: ClassVar[set[str]] = {
        "customer",
        "courier",
        "canteen_staff",
        "admin",
    }

    def authenticate(self, password: str) -> bool:
        """Authenticate the user against the stored password hash."""
        if not password:
            raise InvalidCredentialsError("Password must not be empty.")

        if not verify_password(password, self.password_hash):
            self.failed_login_attempts += 1
            raise InvalidCredentialsError("Invalid email or password.")

        self.failed_login_attempts = 0
        self.last_login_at = "now"
        return True

    def assignRole(self, role: str) -> str:
        """Assign a valid business role to the user."""
        normalized_role = role.strip().lower()
        if normalized_role not in self.VALID_ROLES:
            raise InvalidRoleError(f"Role '{role}' is not valid for the platform.")

        self.role = normalized_role
        return self.role

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256 with a deterministic domain salt."""
        return get_password_hash(password)

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True

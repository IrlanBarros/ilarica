"""Invitation keys for access control."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.exceptions import (
    InvitationKeyAlreadyUsedError,
    InvitationKeyExpiredError,
    InvitationKeyNotUsableError,
)


@dataclass
class InvitationKey:
    """Entity used to validate an invitation and its usage lifecycle."""

    key: str
    issued_to_email: str
    expires_at: datetime
    used_by_user_id: str | None = None
    is_used: bool = False
    is_expired: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def generateKey(cls, issued_to_email: str, valid_for_hours: int = 48) -> "InvitationKey":
        """Create a new invitation key for a destination email."""
        if not issued_to_email or "@" not in issued_to_email:
            raise ValueError("A valid email address is required to create an invitation key.")

        expires_at = datetime.now(timezone.utc) + timedelta(hours=valid_for_hours)
        return cls(
            key=f"ILR-{uuid4().hex[:12].upper()}",
            issued_to_email=issued_to_email,
            expires_at=expires_at,
        )

    def validateUsage(self) -> bool:
        """Validate the key and raise domain exceptions when it is unusable."""
        if self.is_expired or datetime.now(timezone.utc) > self.expires_at:
            self.is_expired = True
            raise InvitationKeyExpiredError("This invitation key has expired.")

        if self.is_used:
            raise InvitationKeyAlreadyUsedError("This invitation key has already been used.")

        if not self.issued_to_email:
            raise InvitationKeyNotUsableError("This invitation key is missing an email target.")

        return True

    def expireKey(self) -> None:
        """Expire a key immediately."""
        self.is_expired = True
        self.is_used = False

    def consume(self, user_id: str) -> None:
        """Consume a valid key once it is used by a user."""
        self.validateUsage()
        self.used_by_user_id = user_id
        self.is_used = True

    def __str__(self) -> str:
        return self.key

"""Use case for user registration in the closed ecosystem."""

from __future__ import annotations

from dataclasses import dataclass
import re
from uuid import uuid4

from app.application.ports.repositories import IInvitationKeyRepository, IUserRepository
from app.core.security import get_password_hash
from app.domain.access_identity.institutional_email import InstitutionalEmail
from app.domain.access_identity.user import User
from app.domain.exceptions import InvitationKeyExpiredError, InvalidInstitutionalEmailError, InvalidRoleError


@dataclass
class RegisterUserUseCase:
    """Register a new user only when allowed by the campus ecosystem rules."""

    user_repository: IUserRepository
    invitation_key_repository: IInvitationKeyRepository

    def execute(
        self,
        name: str,
        email: str,
        whatsapp: str,
        password: str,
        role: str = "customer",
        invitation_key_value: str | None = None,
    ) -> User:
        """Create a user validated by institutional email or an active invitation key."""
        cleaned_name = name.strip()
        cleaned_email = email.strip().lower()
        normalized_whatsapp = re.sub(r"\D", "", whatsapp)
        if len(cleaned_name) < 2:
            raise ValueError("A valid name is required to register a user.")
        if not cleaned_email or "@" not in cleaned_email:
            raise ValueError("A valid email is required to register a user.")
        if not 12 <= len(normalized_whatsapp) <= 15:
            raise ValueError("WhatsApp must include DDI and DDD and contain 12 to 15 digits.")

        existing_user = self.user_repository.get_by_email(cleaned_email)
        if existing_user is not None:
            raise ValueError("A user already exists with this email.")

        valid_key = None
        if invitation_key_value is not None:
            valid_key = self.invitation_key_repository.get_by_value(invitation_key_value)
            if valid_key is None:
                raise ValueError("The provided invitation key does not exist.")
            try:
                valid_key.validateUsage()
            except InvitationKeyExpiredError as exc:
                raise ValueError("The provided invitation key is expired.") from exc

        if role in {"customer", "courier"}:
            try:
                InstitutionalEmail(cleaned_email)
            except InvalidInstitutionalEmailError as exc:
                raise ValueError(
                    "Customer and courier accounts require an @aluno.ufca.edu.br or @ufca.edu.br email."
                ) from exc

        user = User(
            id=uuid4(),
            name=cleaned_name,
            email=cleaned_email,
            whatsapp=normalized_whatsapp,
            password_hash=get_password_hash(password),
            role=role,
        )

        try:
            user.assignRole(role)
        except InvalidRoleError as exc:
            raise ValueError("The institution role selected is invalid.") from exc

        if valid_key is not None:
            valid_key.consume(user.id)
            self.invitation_key_repository.save(valid_key)

        return self.user_repository.add(user)

"""Use case for user registration in the closed ecosystem."""

from __future__ import annotations

from dataclasses import dataclass

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
        email: str,
        password: str,
        role: str = "customer",
        invitation_key_value: str | None = None,
    ) -> User:
        """Create a user validated by institutional email or an active invitation key."""
        cleaned_email = email.strip().lower()
        if not cleaned_email or "@" not in cleaned_email:
            raise ValueError("A valid email is required to register a user.")

        existing_user = self.user_repository.get_by_email(cleaned_email)
        if existing_user is not None:
            raise ValueError("A user already exists with this email.")

        is_institutional = cleaned_email.endswith("@university.edu") or cleaned_email.endswith("@campus.edu")
        valid_key = None
        if invitation_key_value is not None:
            valid_key = self.invitation_key_repository.get_by_value(invitation_key_value)
            if valid_key is None:
                raise ValueError("The provided invitation key does not exist.")
            try:
                valid_key.validateUsage()
            except InvitationKeyExpiredError as exc:
                raise ValueError("The provided invitation key is expired.") from exc

        try:
            InstitutionalEmail(cleaned_email)
            is_institutional = True
        except InvalidInstitutionalEmailError:
            is_institutional = False

        if not is_institutional and valid_key is None:
            raise ValueError("Registration requires an institutional email or a valid invitation key.")

        user = User(
            id=f"user-{cleaned_email}",
            email=cleaned_email,
            password_hash=get_password_hash(password),
            role=role,
        )

        if valid_key is not None:
            try:
                user.assignRole(role)
            except InvalidRoleError as exc:
                raise ValueError("The institution role selected is invalid.") from exc
            valid_key.consume(user.id)
            self.invitation_key_repository.save(valid_key)

        return self.user_repository.add(user)

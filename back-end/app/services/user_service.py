"""Business services for user-related operations.

Services orchestrate domain logic and use repository ports for persistence.
They validate input and translate domain errors into controlled exceptions
when necessary.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.repositories import IInvitationKeyRepository, IUserRepository
from app.domain.access_identity.user import User
from app.domain.exceptions import InvalidRoleError


@dataclass
class UserService:
    """Encapsulates user-related business rules.

    Attributes:
        user_repo: IUserRepository
        invitation_repo: IInvitationKeyRepository
    """

    user_repo: IUserRepository
    invitation_repo: IInvitationKeyRepository

    def register(self, email: str, password: str, role: str = "customer", invitation_key: str | None = None) -> User:
        """Register a new user using validation rules and persistence.

        This method delegates the heavy lifting to the existing
        `RegisterUserUseCase` in application layer where appropriate, but
        performs an additional high-level coordination when necessary.
        """
        from app.application.use_cases.register_user import RegisterUserUseCase

        use_case = RegisterUserUseCase(self.user_repo, self.invitation_repo)
        return use_case.execute(email=email, password=password, role=role, invitation_key_value=invitation_key)

    def change_role(self, user_id: str, new_role: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        try:
            user.assignRole(new_role)
        except InvalidRoleError as exc:
            raise ValueError("Invalid role") from exc
        return self.user_repo.save(user)

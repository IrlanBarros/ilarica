from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.application.use_cases.register_user import RegisterUserUseCase


@pytest.fixture
def user_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def invitation_key_repository() -> MagicMock:
    return MagicMock()


def test_register_user_use_case_accepts_institutional_email(user_repository: MagicMock, invitation_key_repository: MagicMock) -> None:
    # Arrange
    user_repository.get_by_email.return_value = None
    user_repository.add.side_effect = lambda user: user
    use_case = RegisterUserUseCase(user_repository, invitation_key_repository)

    # Act
    result = use_case.execute(
        "Student Name",
        "student@ufca.edu.br",
        "+55 (88) 99999-9999",
        "secure-password",
    )

    # Assert
    assert result.email == "student@ufca.edu.br"
    assert result.name == "Student Name"
    assert result.whatsapp == "5588999999999"
    assert result.id.version == 4
    assert result.role == "customer"
    user_repository.add.assert_called_once()
    invitation_key_repository.get_by_value.assert_not_called()


def test_register_user_use_case_accepts_generic_email_for_admin_internal_flow(
    user_repository: MagicMock,
    invitation_key_repository: MagicMock,
) -> None:
    # Arrange
    user_repository.get_by_email.return_value = None
    user_repository.add.side_effect = lambda user: user
    use_case = RegisterUserUseCase(user_repository, invitation_key_repository)
    result = use_case.execute(
        "Internal Admin",
        "admin@business.com",
        "5588999999998",
        "secure-password",
        role="admin",
    )

    assert result.email == "admin@business.com"
    assert result.role == "admin"


def test_register_user_use_case_rejects_invalid_email_without_institutional_or_key(
    user_repository: MagicMock,
    invitation_key_repository: MagicMock,
) -> None:
    # Arrange
    user_repository.get_by_email.return_value = None
    invitation_key_repository.get_by_value.return_value = None
    use_case = RegisterUserUseCase(user_repository, invitation_key_repository)

    # Act / Assert
    with pytest.raises(ValueError, match="Customer and courier accounts require"):
        use_case.execute(
            "Invalid Student",
            "student@gmail.com",
            "5588999999997",
            "secure-password",
        )

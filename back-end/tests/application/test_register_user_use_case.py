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
    result = use_case.execute("student@ufca.edu.br", "secure-password")

    # Assert
    assert result.email == "student@ufca.edu.br"
    assert result.role == "customer"
    user_repository.add.assert_called_once()
    invitation_key_repository.get_by_value.assert_not_called()


def test_register_user_use_case_accepts_valid_invitation_key_when_email_is_not_institutional(
    user_repository: MagicMock,
    invitation_key_repository: MagicMock,
) -> None:
    # Arrange
    user_repository.get_by_email.return_value = None
    invitation_key_repository.get_by_value.return_value = MagicMock(
        key="ILR-ABC123",
        validateUsage=MagicMock(return_value=True),
        consume=MagicMock(),
    )
    user_repository.add.side_effect = lambda user: user
    use_case = RegisterUserUseCase(user_repository, invitation_key_repository)

    # Act
    result = use_case.execute("student@gmail.com", "secure-password", invitation_key_value="ILR-ABC123")

    # Assert
    assert result.email == "student@gmail.com"
    invitation_key_repository.get_by_value.assert_called_once_with("ILR-ABC123")
    invitation_key_repository.save.assert_called_once()


def test_register_user_use_case_rejects_invalid_email_without_institutional_or_key(
    user_repository: MagicMock,
    invitation_key_repository: MagicMock,
) -> None:
    # Arrange
    user_repository.get_by_email.return_value = None
    invitation_key_repository.get_by_value.return_value = None
    use_case = RegisterUserUseCase(user_repository, invitation_key_repository)

    # Act / Assert
    with pytest.raises(ValueError, match="institutional email or a valid invitation key"):
        use_case.execute("student@gmail.com", "secure-password")

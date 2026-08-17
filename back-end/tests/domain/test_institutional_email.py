from __future__ import annotations

import pytest

from app.domain.access_identity.institutional_email import InstitutionalEmail
from app.domain.exceptions import InvalidInstitutionalEmailError


@pytest.fixture
def valid_institutional_email() -> InstitutionalEmail:
    return InstitutionalEmail("student@ufca.edu.br")


def test_institutional_email_accepts_ufca_domain(valid_institutional_email: InstitutionalEmail) -> None:
    # Arrange
    email = valid_institutional_email

    # Act
    normalized = email.value
    domain = email.domain

    # Assert
    assert normalized == "student@ufca.edu.br"
    assert domain == "ufca.edu.br"
    assert email.is_allowed() is True


def test_institutional_email_accepts_student_domain() -> None:
    # Arrange
    email_value = "student@aluno.ufca.edu.br"

    # Act
    email = InstitutionalEmail(email_value)

    # Assert
    assert email.value == "student@aluno.ufca.edu.br"
    assert email.domain == "aluno.ufca.edu.br"
    assert email.is_allowed() is True


def test_institutional_email_rejects_non_institutional_domains() -> None:
    # Arrange
    invalid_emails = [
        "student@gmail.com",
        "student@ufca.com",
        "student@outro.edu",
        "not-an-email",
    ]

    # Act / Assert
    for email_value in invalid_emails:
        with pytest.raises(InvalidInstitutionalEmailError):
            InstitutionalEmail(email_value)

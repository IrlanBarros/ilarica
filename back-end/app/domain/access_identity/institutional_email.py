"""Institutional email value object for the closed university ecosystem."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import InvalidInstitutionalEmailError


@dataclass(frozen=True)
class InstitutionalEmail:
    """Immutable value object for validated university email addresses."""

    value: str

    ALLOWED_DOMAINS: tuple[str, ...] = ("ufca.edu.br", "aluno.ufca.edu.br")

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized or "@" not in normalized:
            raise InvalidInstitutionalEmailError("Institutional email must have a valid email format.")

        domain = normalized.split("@", 1)[1]
        if domain not in self.ALLOWED_DOMAINS:
            raise InvalidInstitutionalEmailError(
                "Institutional email must use one of the approved university domains: "
                "ufca.edu.br or aluno.ufca.edu.br."
            )

        object.__setattr__(self, "value", normalized)

    @property
    def domain(self) -> str:
        return self.value.split("@", 1)[1]

    def is_allowed(self) -> bool:
        return self.domain in self.ALLOWED_DOMAINS

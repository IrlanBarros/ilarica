"""Strict contracts for institutional email verification."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user_schemas import _EMAIL_RE


class EmailVerificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise ValueError("Invalid email format")
        return normalized


class EmailVerificationConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(..., min_length=32, max_length=256)


class EmailVerificationMessage(BaseModel):
    detail: str

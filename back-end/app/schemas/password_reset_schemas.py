"""Strict contracts for the password recovery flow."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user_schemas import _EMAIL_RE


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise ValueError("Invalid email format")
        return normalized


class PasswordResetConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(..., min_length=32, max_length=256)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(character.isupper() for character in value) or not any(character.isdigit() for character in value):
            raise ValueError("Password must contain at least one uppercase letter and one number")
        return value


class PasswordResetMessage(BaseModel):
    detail: str

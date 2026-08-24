"""Pydantic schemas for the user domain."""

from __future__ import annotations

import re
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class UserBase(BaseModel):
    """Common user attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    email: str
    whatsapp: str
    role: str = Field(default="customer", min_length=2, max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip()
        if not _EMAIL_RE.match(normalized):
            raise ValueError("Invalid email format")
        return normalized.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed_roles = {"customer", "courier", "canteen_staff", "admin"}
        normalized = value.strip().lower()
        if normalized not in allowed_roles:
            raise ValueError("Role must be one of: customer, courier, canteen_staff, admin")
        return normalized

    @field_validator("whatsapp")
    @classmethod
    def normalize_whatsapp(cls, value: str) -> str:
        normalized = re.sub(r"\D", "", value)
        if not 12 <= len(normalized) <= 15:
            raise ValueError("WhatsApp must include DDI and DDD and contain 12 to 15 digits")
        return normalized


class UserCreate(UserBase):
    """Attributes required to create a user."""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must contain at least 8 characters")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        return value

    @model_validator(mode="after")
    def validate_institutional_email_for_public_roles(self) -> "UserCreate":
        if self.role in {"customer", "courier"} and not self.email.endswith(
            ("@aluno.ufca.edu.br", "@ufca.edu.br")
        ):
            raise ValueError(
                "Customer and courier accounts require an @aluno.ufca.edu.br or @ufca.edu.br email"
            )
        return self


class UserUpdate(BaseModel):
    """Optional attributes for partial user updates."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    role: Optional[str] = Field(default=None, min_length=2, max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not _EMAIL_RE.match(normalized):
            raise ValueError("Invalid email format")
        return normalized.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed_roles = {"customer", "courier", "canteen_staff", "admin"}
        normalized = value.strip().lower()
        if normalized not in allowed_roles:
            raise ValueError("Role must be one of: customer, courier, canteen_staff, admin")
        return normalized

    @field_validator("whatsapp")
    @classmethod
    def normalize_whatsapp(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = re.sub(r"\D", "", value)
        if not 12 <= len(normalized) <= 15:
            raise ValueError("WhatsApp must include DDI and DDD and contain 12 to 15 digits")
        return normalized


class UserResponse(UserBase):
    """User output schema."""

    id: UUID
    is_active: bool
    is_email_validated: bool
    model_config = ConfigDict(from_attributes=True)


SchemaBase = UserBase
SchemaCreate = UserCreate
SchemaUpdate = UserUpdate
SchemaResponse = UserResponse

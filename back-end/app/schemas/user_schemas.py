"""Pydantic schemas for the user domain."""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class UserBase(BaseModel):
    """Common user attributes."""

    name: str = Field(..., min_length=2, max_length=150)
    email: str
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


class UserUpdate(BaseModel):
    """Optional attributes for partial user updates."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[str] = None
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


class UserResponse(UserBase):
    """User output schema."""

    id: str
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


SchemaBase = UserBase
SchemaCreate = UserCreate
SchemaUpdate = UserUpdate
SchemaResponse = UserResponse

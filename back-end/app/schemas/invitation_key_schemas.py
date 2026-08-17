"""Pydantic schemas for invitation keys."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InvitationKeyBase(BaseModel):
    """Common invitation key attributes."""

    key: str = Field(..., min_length=6, max_length=50)
    issued_to_email: str = Field(..., min_length=5, max_length=255)
    expires_at: datetime
    is_used: bool = False
    is_expired: bool = False

    @field_validator("issued_to_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip()
        if "@" not in normalized:
            raise ValueError("issued_to_email must be a valid email address")
        return normalized.lower()


class InvitationKeyCreate(InvitationKeyBase):
    """Attributes required to create an invitation key."""


class InvitationKeyUpdate(BaseModel):
    """Optional attributes for partial updates."""

    key: Optional[str] = Field(default=None, min_length=6, max_length=50)
    issued_to_email: Optional[str] = Field(default=None, min_length=5, max_length=255)
    expires_at: Optional[datetime] = None
    is_used: Optional[bool] = None
    is_expired: Optional[bool] = None

    @field_validator("issued_to_email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if "@" not in normalized:
            raise ValueError("issued_to_email must be a valid email address")
        return normalized.lower()


class InvitationKeyResponse(InvitationKeyBase):
    """Invitation key output schema."""

    id: str
    used_by_user_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


SchemaBase = InvitationKeyBase
SchemaCreate = InvitationKeyCreate
SchemaUpdate = InvitationKeyUpdate
SchemaResponse = InvitationKeyResponse

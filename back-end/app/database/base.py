"""SQLAlchemy base configuration for the infrastructure layer."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common declarative base for all SQLAlchemy models."""

    pass

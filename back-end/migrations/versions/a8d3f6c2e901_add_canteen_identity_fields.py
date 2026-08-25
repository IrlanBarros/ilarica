"""Persist required canteen identity fields.

Revision ID: a8d3f6c2e901
Revises: c4b713ad9e20
Create Date: 2026-08-23 23:45:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a8d3f6c2e901"
down_revision: str | Sequence[str] | None = "c4b713ad9e20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add non-null name and location columns without breaking legacy rows."""
    op.add_column(
        "canteens",
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
            server_default="Cantina em atualização",
        ),
    )
    op.add_column(
        "canteens",
        sa.Column(
            "location",
            sa.String(length=200),
            nullable=False,
            server_default="Local em atualização",
        ),
    )
    op.alter_column("canteens", "name", server_default=None)
    op.alter_column("canteens", "location", server_default=None)


def downgrade() -> None:
    """Remove persisted canteen identity fields."""
    op.drop_column("canteens", "location")
    op.drop_column("canteens", "name")

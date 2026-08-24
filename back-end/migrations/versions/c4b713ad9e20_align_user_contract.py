"""Align the persisted user contract with the public API.

Revision ID: c4b713ad9e20
Revises: 7f8c4a12b9d1
Create Date: 2026-08-23 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4b713ad9e20"
down_revision: str | Sequence[str] | None = "7f8c4a12b9d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the missing user fields while preserving the UUID identity contract."""
    op.add_column(
        "users",
        sa.Column("whatsapp", sa.String(length=15), nullable=False, server_default=""),
    )
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("users", "whatsapp", server_default=None)

    # users.id and every foreign key that references it were created as native
    # UUID columns in the initial migration. This revision intentionally keeps
    # that database type and aligns the SQLAlchemy mapping with it.


def downgrade() -> None:
    """Remove fields introduced by this contract alignment."""
    op.drop_column("users", "is_active")
    op.drop_column("users", "whatsapp")

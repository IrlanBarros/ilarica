"""Persist the Pix provider used by each transaction.

Revision ID: c4e7b2a109fd
Revises: f9c2d4a71b30
Create Date: 2026-08-24 13:10:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4e7b2a109fd"
down_revision: str | Sequence[str] | None = "f9c2d4a71b30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "payment_transactions",
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="internal"),
    )


def downgrade() -> None:
    op.drop_column("payment_transactions", "provider")

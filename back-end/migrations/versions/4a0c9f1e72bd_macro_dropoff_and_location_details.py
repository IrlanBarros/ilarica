"""Align macro drop-off zones and order delivery details.

Revision ID: 4a0c9f1e72bd
Revises: d91e74c3a8b2
Create Date: 2026-08-25 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4a0c9f1e72bd"
down_revision: str | Sequence[str] | None = "d91e74c3a8b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("drop_off_zones", "capacity", new_column_name="capacity_total")
    op.add_column("orders", sa.Column("location_details", sa.String(length=180), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "location_details")
    op.alter_column("drop_off_zones", "capacity_total", new_column_name="capacity")
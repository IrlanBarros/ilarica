"""Add seller catalog metadata and pickup fulfillment.

Revision ID: d7a4e2c18b61
Revises: c4e7b2a109fd
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7a4e2c18b61"
down_revision: str | Sequence[str] | None = "c4e7b2a109fd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("canteens", sa.Column("opening_hours", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("products", sa.Column("image_url", sa.String(length=500), nullable=True))
    op.add_column("orders", sa.Column("fulfillment_type", sa.String(length=20), nullable=False, server_default="delivery"))
    op.alter_column("orders", "drop_off_zone_id", existing_type=sa.UUID(), nullable=True)
    op.create_check_constraint(
        "ck_orders_fulfillment_destination",
        "orders",
        "(fulfillment_type = 'pickup' AND drop_off_zone_id IS NULL) OR "
        "(fulfillment_type = 'delivery' AND drop_off_zone_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_orders_fulfillment_destination", "orders", type_="check")
    op.execute("DELETE FROM orders WHERE drop_off_zone_id IS NULL")
    op.alter_column("orders", "drop_off_zone_id", existing_type=sa.UUID(), nullable=False)
    op.drop_column("orders", "fulfillment_type")
    op.drop_column("products", "image_url")
    op.drop_column("canteens", "opening_hours")

"""add product category and available stock

Revision ID: b6a14f209c72
Revises: e2d8a913c441
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b6a14f209c72"
down_revision: str | Sequence[str] | None = "e2d8a913c441"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("category", sa.String(length=30), nullable=False, server_default="outros"),
    )
    op.add_column(
        "products",
        sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="20"),
    )
    op.create_check_constraint(
        "ck_products_stock_quantity_non_negative",
        "products",
        "stock_quantity >= 0",
    )
    op.alter_column("products", "category", server_default=None)
    op.alter_column("products", "stock_quantity", server_default=None)


def downgrade() -> None:
    op.drop_constraint("ck_products_stock_quantity_non_negative", "products", type_="check")
    op.drop_column("products", "stock_quantity")
    op.drop_column("products", "category")

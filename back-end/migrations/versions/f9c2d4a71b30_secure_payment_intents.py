"""Secure payment intents with idempotency and Pix lifecycle fields.

Revision ID: f9c2d4a71b30
Revises: a8d3f6c2e901
Create Date: 2026-08-24 12:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f9c2d4a71b30"
down_revision: str | Sequence[str] | None = "a8d3f6c2e901"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add immutable payment lifecycle and idempotency fields."""
    op.add_column("payment_transactions", sa.Column("idempotency_key", sa.String(length=128), nullable=True))
    op.add_column("payment_transactions", sa.Column("pix_copy_paste", sa.Text(), nullable=True))
    op.add_column("payment_transactions", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("payment_transactions", sa.Column("failure_reason", sa.String(length=255), nullable=True))
    op.add_column(
        "payment_transactions",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("payment_transactions", sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        "UPDATE payment_transactions "
        "SET idempotency_key = 'legacy-' || id::text "
        "WHERE idempotency_key IS NULL"
    )
    op.alter_column("payment_transactions", "idempotency_key", nullable=False)
    op.execute(
        "DELETE FROM payment_transactions duplicate "
        "USING payment_transactions keeper "
        "WHERE duplicate.order_id = keeper.order_id AND duplicate.id > keeper.id"
    )
    op.create_unique_constraint(
        "uq_payment_transactions_idempotency_key",
        "payment_transactions",
        ["idempotency_key"],
    )
    op.create_unique_constraint(
        "uq_payment_transactions_order_id",
        "payment_transactions",
        ["order_id"],
    )


def downgrade() -> None:
    """Remove payment intent lifecycle fields."""
    op.drop_constraint("uq_payment_transactions_order_id", "payment_transactions", type_="unique")
    op.drop_constraint("uq_payment_transactions_idempotency_key", "payment_transactions", type_="unique")
    op.drop_column("payment_transactions", "confirmed_at")
    op.drop_column("payment_transactions", "created_at")
    op.drop_column("payment_transactions", "failure_reason")
    op.drop_column("payment_transactions", "expires_at")
    op.drop_column("payment_transactions", "pix_copy_paste")
    op.drop_column("payment_transactions", "idempotency_key")

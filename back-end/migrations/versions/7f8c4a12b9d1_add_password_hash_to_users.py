"""add password_hash to users

Revision ID: 7f8c4a12b9d1
Revises: 209d0c5ad060
Create Date: 2026-08-16 23:10:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f8c4a12b9d1"
down_revision: Union[str, Sequence[str], None] = "209d0c5ad060"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=128), nullable=False, server_default=""),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password_hash")

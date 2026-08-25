"""add canteen onboarding and moderation

Revision ID: d91e74c3a8b2
Revises: c83d1f7a2e64
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d91e74c3a8b2"
down_revision: str | Sequence[str] | None = "c83d1f7a2e64"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("canteens", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("canteens", sa.Column("logo_url", sa.String(500), nullable=True))
    op.add_column(
        "canteens", sa.Column("commercial_terms_accepted_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "canteens",
        sa.Column("moderation_status", sa.String(20), nullable=False, server_default="approved"),
    )
    op.add_column("canteens", sa.Column("moderation_reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("canteens", sa.Column("moderated_by_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("canteens", sa.Column("rejection_reason", sa.String(500), nullable=True))
    op.create_foreign_key(
        "fk_canteens_moderated_by_users",
        "canteens",
        "users",
        ["moderated_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_canteens_moderation_status",
        "canteens",
        "moderation_status IN ('pending', 'approved', 'rejected')",
    )
    op.alter_column("canteens", "moderation_status", server_default=None)


def downgrade() -> None:
    op.drop_constraint("ck_canteens_moderation_status", "canteens", type_="check")
    op.drop_constraint("fk_canteens_moderated_by_users", "canteens", type_="foreignkey")
    op.drop_column("canteens", "rejection_reason")
    op.drop_column("canteens", "moderated_by_id")
    op.drop_column("canteens", "moderation_reviewed_at")
    op.drop_column("canteens", "moderation_status")
    op.drop_column("canteens", "commercial_terms_accepted_at")
    op.drop_column("canteens", "logo_url")
    op.drop_column("canteens", "description")

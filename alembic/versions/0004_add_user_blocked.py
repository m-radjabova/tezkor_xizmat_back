"""add user blocked flag

Revision ID: 0004_add_user_blocked
Revises: 0003_add_review_approval
Create Date: 2026-09-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0004_add_user_blocked"
down_revision: str | None = "0003_add_review_approval"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_blocked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_index(op.f("ix_users_is_blocked"), "users", ["is_blocked"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_is_blocked"), table_name="users")
    op.drop_column("users", "is_blocked")

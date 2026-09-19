"""add review approval

Revision ID: 0003_add_review_approval
Revises: 0002_add_business_working_days
Create Date: 2026-09-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0003_add_review_approval"
down_revision: str | None = "0002_add_business_working_days"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reviews",
        sa.Column("is_approved", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_index(op.f("ix_reviews_is_approved"), "reviews", ["is_approved"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_is_approved"), table_name="reviews")
    op.drop_column("reviews", "is_approved")

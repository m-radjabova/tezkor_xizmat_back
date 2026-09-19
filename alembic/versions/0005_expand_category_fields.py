"""expand category name and icon fields

Revision ID: 0005_expand_category_fields
Revises: 0004_add_user_blocked
Create Date: 2026-09-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0005_expand_category_fields"
down_revision: str | None = "0004_add_user_blocked"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("categories", "name", existing_type=sa.String(length=100), type_=sa.String(length=255))
    op.alter_column("categories", "icon", existing_type=sa.String(length=100), type_=sa.String(length=255))


def downgrade() -> None:
    op.alter_column("categories", "icon", existing_type=sa.String(length=255), type_=sa.String(length=100))
    op.alter_column("categories", "name", existing_type=sa.String(length=255), type_=sa.String(length=100))
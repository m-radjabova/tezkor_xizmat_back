"""add business working days

Revision ID: 0002_add_business_working_days
Revises: 0001_tezkor_xizmat_init
Create Date: 2026-09-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0002_add_business_working_days"
down_revision: str | None = "0001_tezkor_xizmat_init"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("businesses", sa.Column("working_days", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("businesses", "working_days")

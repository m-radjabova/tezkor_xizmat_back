"""legacy user preferences placeholder

Revision ID: legacy_0002
Revises: legacy_0001
Create Date: 2026-09-17
"""

from collections.abc import Sequence


revision: str = "legacy_0002"
down_revision: str | None = "legacy_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

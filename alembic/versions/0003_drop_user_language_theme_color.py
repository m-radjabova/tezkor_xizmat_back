"""legacy drop user preferences placeholder

Revision ID: legacy_0003
Revises: legacy_0002
Create Date: 2026-09-17
"""

from collections.abc import Sequence


revision: str = "legacy_0003"
down_revision: str | None = "legacy_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

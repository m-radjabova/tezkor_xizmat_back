"""tezkor xizmat init

Revision ID: 0001_tezkor_xizmat_init
Revises: legacy_0004
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0001_tezkor_xizmat_init"
down_revision: str | None = "legacy_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for table_name in (
        "notifications",
        "recurring_transactions",
        "transactions",
        "savings_goals",
        "debts",
        "notes",
        "budgets",
        "categories",
        "users",
    ):
        op.execute(sa.text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
    op.execute(sa.text("DROP TYPE IF EXISTS user_role CASCADE"))

    user_role = postgresql.ENUM("customer", "provider", "admin", name="user_role", create_type=False)
    user_role_create = postgresql.ENUM("customer", "provider", "admin", name="user_role")
    user_role_create.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("firebase_uid", sa.String(length=128), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("organization_name", sa.String(length=150), nullable=True),
        sa.Column("responsible_person", sa.String(length=100), nullable=True),
        sa.Column("provider_category_ids", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_firebase_uid"), "users", ["firebase_uid"], unique=True)
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("icon", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)

    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("logo_url", sa.String(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("open_time", sa.Time(), nullable=True),
        sa.Column("close_time", sa.Time(), nullable=True),
        sa.Column("images", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_businesses_category_id"), "businesses", ["category_id"], unique=False)
    op.create_index(op.f("ix_businesses_is_verified"), "businesses", ["is_verified"], unique=False)
    op.create_index(op.f("ix_businesses_name"), "businesses", ["name"], unique=False)
    op.create_index(op.f("ix_businesses_owner_id"), "businesses", ["owner_id"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "user_id", name="uq_reviews_business_user"),
    )
    op.create_index(op.f("ix_reviews_business_id"), "reviews", ["business_id"], unique=False)
    op.create_index(op.f("ix_reviews_user_id"), "reviews", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_user_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_business_id"), table_name="reviews")
    op.drop_table("reviews")
    op.drop_index(op.f("ix_businesses_owner_id"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_name"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_is_verified"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_category_id"), table_name="businesses")
    op.drop_table("businesses")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.drop_index(op.f("ix_users_firebase_uid"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.execute(sa.text("DROP TYPE IF EXISTS user_role"))

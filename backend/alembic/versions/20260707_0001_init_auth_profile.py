"""init auth and profile tables

Revision ID: 20260707_0001
Revises: None
Create Date: 2026-07-07 14:05:00
"""

import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


DEFAULT_LAYOUT = [
    {"id": "media_block", "active": True},
    {"id": "booking_block", "active": True},
    {"id": "products_block", "active": True},
    {"id": "affiliate_block", "active": True},
]


revision = "20260707_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("auth_provider", sa.String(length=50), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("display_name", sa.String(length=150), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("theme_mode", sa.String(length=50), nullable=False),
        sa.Column("font_family", sa.String(length=100), nullable=False),
        sa.Column("primary_color", sa.String(length=20), nullable=False),
        sa.Column("text_color", sa.String(length=20), nullable=False),
        sa.Column("bg_type", sa.String(length=50), nullable=False),
        sa.Column("bg_value", sa.Text(), nullable=True),
        sa.Column("avatar_style", sa.String(length=50), nullable=False),
        sa.Column("button_style", sa.String(length=50), nullable=False),
        sa.Column(
            "layout_structure",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text(f"'{json.dumps(DEFAULT_LAYOUT)}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_user_profiles_username"), "user_profiles", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_profiles_username"), table_name="user_profiles")
    op.drop_table("user_profiles")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

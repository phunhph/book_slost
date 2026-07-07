"""seed initial demo data

Revision ID: 20260707_0002
Revises: 20260707_0001
Create Date: 2026-07-07 14:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260707_0002"
down_revision = "20260707_0001"
branch_labels = None
depends_on = None


USER_TABLE = sa.table(
    "users",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("email", sa.String(length=255)),
    sa.column("password_hash", sa.String(length=255)),
    sa.column("auth_provider", sa.String(length=50)),
    sa.column("role", sa.String(length=50)),
    sa.column("is_active", sa.Boolean()),
)

PROFILE_TABLE = sa.table(
    "user_profiles",
    sa.column("user_id", postgresql.UUID(as_uuid=True)),
    sa.column("username", sa.String(length=100)),
    sa.column("display_name", sa.String(length=150)),
    sa.column("bio", sa.Text()),
    sa.column("avatar_url", sa.Text()),
    sa.column("theme_mode", sa.String(length=50)),
    sa.column("font_family", sa.String(length=100)),
    sa.column("primary_color", sa.String(length=20)),
    sa.column("text_color", sa.String(length=20)),
    sa.column("bg_type", sa.String(length=50)),
    sa.column("bg_value", sa.Text()),
    sa.column("avatar_style", sa.String(length=50)),
    sa.column("button_style", sa.String(length=50)),
    sa.column("layout_structure", postgresql.JSONB(astext_type=sa.Text())),
)


ADMIN_USER_ID = "11111111-1111-1111-1111-111111111111"
CREATOR_USER_ID = "22222222-2222-2222-2222-222222222222"

DEFAULT_LAYOUT = [
    {"id": "media_block", "active": True},
    {"id": "booking_block", "active": True},
    {"id": "products_block", "active": True},
    {"id": "affiliate_block", "active": True},
]


def upgrade() -> None:
    op.bulk_insert(
        USER_TABLE,
        [
            {
                "id": ADMIN_USER_ID,
                "email": "admin@example.com",
                "password_hash": "$2b$12$demo.demo.demo.demo.demo.demo.demo.demo.demo.demo",
                "auth_provider": "local",
                "role": "admin",
                "is_active": True,
            },
            {
                "id": CREATOR_USER_ID,
                "email": "creator@example.com",
                "password_hash": "$2b$12$demo.demo.demo.demo.demo.demo.demo.demo.demo.demo",
                "auth_provider": "local",
                "role": "kol",
                "is_active": True,
            },
        ],
    )

    op.bulk_insert(
        PROFILE_TABLE,
        [
            {
                "user_id": ADMIN_USER_ID,
                "username": "admin-demo",
                "display_name": "Admin Demo",
                "bio": "Tai khoan admin mau de kiem tra dashboard va luong quan tri.",
                "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=500&q=80",
                "theme_mode": "light",
                "font_family": "Inter",
                "primary_color": "#0F172A",
                "text_color": "#111111",
                "bg_type": "color",
                "bg_value": "#F8FAFC",
                "avatar_style": "circle",
                "button_style": "filled",
                "layout_structure": DEFAULT_LAYOUT,
            },
            {
                "user_id": CREATOR_USER_ID,
                "username": "creator-demo",
                "display_name": "Creator Demo",
                "bio": "Ho so cong khai mau de kiem tra client UI va dynamic profile layout.",
                "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=500&q=80",
                "theme_mode": "custom",
                "font_family": "Inter",
                "primary_color": "#FF007F",
                "text_color": "#111111",
                "bg_type": "gradient",
                "bg_value": "linear-gradient(135deg, #fdf2f8 0%, #e0f2fe 100%)",
                "avatar_style": "rounded",
                "button_style": "shadow",
                "layout_structure": DEFAULT_LAYOUT,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM user_profiles
            WHERE user_id IN (:admin_user_id, :creator_user_id)
            """
        ).bindparams(admin_user_id=ADMIN_USER_ID, creator_user_id=CREATOR_USER_ID)
    )
    op.execute(
        sa.text(
            """
            DELETE FROM users
            WHERE id IN (:admin_user_id, :creator_user_id)
            """
        ).bindparams(admin_user_id=ADMIN_USER_ID, creator_user_id=CREATOR_USER_ID)
    )

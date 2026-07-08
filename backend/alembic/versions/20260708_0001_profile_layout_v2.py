"""Migrate user_profiles.layout_structure from v1 list to v2 object."""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260708_0001"
down_revision = "20260707_0004"
branch_labels = None
depends_on = None


def _migrate_row(layout_structure, bio, phone, zalo, messenger):
    from app.modules.profile.blocks_v2 import migrate_layout_to_v2

    return migrate_layout_to_v2(
        layout_structure,
        bio=bio,
        phone=phone,
        zalo=zalo,
        messenger=messenger,
    )


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            """
            SELECT user_id, bio, phone, zalo, messenger, layout_structure
            FROM user_profiles
            """
        )
    ).mappings()

    for row in rows:
        layout = row["layout_structure"]
        if isinstance(layout, str):
            layout = json.loads(layout)

        if isinstance(layout, dict) and layout.get("version") == 2:
            continue

        migrated = _migrate_row(layout, row["bio"], row["phone"], row["zalo"], row["messenger"])
        bind.execute(
            sa.text(
                """
                UPDATE user_profiles
                SET layout_structure = CAST(:layout AS JSONB)
                WHERE user_id = :user_id
                """
            ),
            {"layout": json.dumps(migrated), "user_id": row["user_id"]},
        )


def downgrade() -> None:
    default_v1 = [
        {"id": "media_block", "active": True},
        {"id": "booking_block", "active": True},
        {"id": "products_block", "active": True},
        {"id": "affiliate_block", "active": True},
    ]
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE user_profiles
            SET layout_structure = CAST(:layout AS JSONB)
            """
        ),
        {"layout": json.dumps(default_v1)},
    )

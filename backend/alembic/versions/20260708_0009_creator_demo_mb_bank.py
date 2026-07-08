"""update creator-demo bank to MB Bank 0962954690

Revision ID: 20260708_0009
Revises: 20260708_0008
Create Date: 2026-07-08 21:15:00
"""

from __future__ import annotations

from alembic import op


revision = "20260708_0009"
down_revision = "20260708_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE user_profiles AS p
        SET
            bank_name = 'MB Bank',
            bank_code = '970422',
            bank_account_number = '0962954690',
            bank_account_name = COALESCE(NULLIF(TRIM(p.bank_account_name), ''), 'CREATOR DEMO')
        FROM users AS u
        WHERE p.user_id = u.id
          AND u.email = 'creator@example.com'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE user_profiles AS p
        SET
            bank_name = 'Vietcombank (VCB)',
            bank_code = '970436',
            bank_account_number = '0123456789',
            bank_account_name = 'CREATOR DEMO'
        FROM users AS u
        WHERE p.user_id = u.id
          AND u.email = 'creator@example.com'
        """
    )

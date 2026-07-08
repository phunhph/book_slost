"""add kol bank account fields for VietQR payment

Revision ID: 20260708_0004
Revises: 20260708_0003
Create Date: 2026-07-08 19:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260708_0004"
down_revision = "20260708_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("bank_name", sa.String(length=100), nullable=True))
    op.add_column("user_profiles", sa.Column("bank_code", sa.String(length=20), nullable=True))
    op.add_column(
        "user_profiles",
        sa.Column("bank_account_number", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("bank_account_name", sa.String(length=150), nullable=True),
    )

    op.execute(
        """
        UPDATE user_profiles
        SET bank_name = 'Vietcombank',
            bank_code = '970436',
            bank_account_number = '0123456789',
            bank_account_name = 'CREATOR DEMO'
        WHERE username = 'creator-demo'
        """
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "bank_account_name")
    op.drop_column("user_profiles", "bank_account_number")
    op.drop_column("user_profiles", "bank_code")
    op.drop_column("user_profiles", "bank_name")

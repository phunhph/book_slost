"""add kol pricing and booking payment fields

Revision ID: 20260708_0003
Revises: 20260708_0002
Create Date: 2026-07-08 19:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260708_0003"
down_revision = "20260708_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("pricing_type", sa.String(length=30), nullable=False, server_default="match"),
    )
    op.add_column(
        "user_profiles",
        sa.Column("price_per_match", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "user_profiles",
        sa.Column("price_per_hour", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "user_profiles",
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
    )

    op.add_column(
        "bookings",
        sa.Column("pricing_type", sa.String(length=30), nullable=False, server_default="match"),
    )
    op.add_column(
        "bookings",
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "bookings",
        sa.Column("unit_price", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "bookings",
        sa.Column("total_amount", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "bookings",
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
    )
    op.add_column("bookings", sa.Column("payment_qr_url", sa.Text(), nullable=True))
    op.add_column("bookings", sa.Column("payment_code", sa.String(length=50), nullable=True))
    op.add_column(
        "bookings",
        sa.Column("payment_status", sa.String(length=30), nullable=False, server_default="unpaid"),
    )

    op.execute(
        """
        UPDATE user_profiles
        SET pricing_type = 'match',
            price_per_match = 150000,
            price_per_hour = 100000,
            currency = 'VND'
        WHERE username = 'creator-demo'
        """
    )


def downgrade() -> None:
    op.drop_column("bookings", "payment_status")
    op.drop_column("bookings", "payment_code")
    op.drop_column("bookings", "payment_qr_url")
    op.drop_column("bookings", "currency")
    op.drop_column("bookings", "total_amount")
    op.drop_column("bookings", "unit_price")
    op.drop_column("bookings", "quantity")
    op.drop_column("bookings", "pricing_type")

    op.drop_column("user_profiles", "currency")
    op.drop_column("user_profiles", "price_per_hour")
    op.drop_column("user_profiles", "price_per_match")
    op.drop_column("user_profiles", "pricing_type")

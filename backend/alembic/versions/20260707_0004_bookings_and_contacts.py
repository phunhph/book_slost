"""bookings and profile contact fields

Revision ID: 20260707_0004
Revises: 20260707_0003
Create Date: 2026-07-07 19:45:00
"""

from datetime import UTC, datetime, timedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260707_0004"
down_revision = "20260707_0003"
branch_labels = None
depends_on = None

KOL_USER_ID = "22222222-2222-2222-2222-222222222222"
CUSTOMER_USER_ID = "33333333-3333-3333-3333-333333333333"


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column("user_profiles", sa.Column("zalo", sa.String(length=100), nullable=True))
    op.add_column("user_profiles", sa.Column("messenger", sa.String(length=100), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE user_profiles
            SET phone = '0901000001', zalo = 'creator-demo', messenger = 'creator.demo'
            WHERE user_id = '22222222-2222-2222-2222-222222222222'::uuid
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE user_profiles
            SET phone = '0901000002', zalo = 'customer-demo', messenger = 'customer.demo'
            WHERE user_id = '33333333-3333-3333-3333-333333333333'::uuid
            """
        )
    )

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kol_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("guest_name", sa.String(length=150), nullable=True),
        sa.Column("guest_phone", sa.String(length=30), nullable=True),
        sa.Column("guest_zalo", sa.String(length=100), nullable=True),
        sa.Column("guest_messenger", sa.String(length=100), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["kol_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_customer_user_id"), "bookings", ["customer_user_id"], unique=False)
    op.create_index(op.f("ix_bookings_kol_user_id"), "bookings", ["kol_user_id"], unique=False)

    scheduled_at = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    op.execute(
        sa.text(
            f"""
            INSERT INTO bookings (
                id, kol_user_id, customer_user_id, guest_name, guest_phone, guest_zalo,
                guest_messenger, scheduled_at, status, notes
            ) VALUES (
                '44444444-4444-4444-4444-444444444444'::uuid,
                '22222222-2222-2222-2222-222222222222'::uuid,
                '33333333-3333-3333-3333-333333333333'::uuid,
                'Customer Demo',
                '0901000002',
                'customer-demo',
                'customer.demo',
                '{scheduled_at}'::timestamptz,
                'pending',
                'Booking mau de test admin va KOL calendar.'
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_bookings_kol_user_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_customer_user_id"), table_name="bookings")
    op.drop_table("bookings")
    op.drop_column("user_profiles", "messenger")
    op.drop_column("user_profiles", "zalo")
    op.drop_column("user_profiles", "phone")

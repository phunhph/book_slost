"""add booking activity logs

Revision ID: 20260709_0012
Revises: 20260709_0011
Create Date: 2026-07-09 14:58:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_0012"
down_revision = "20260709_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "booking_activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=50), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_booking_activity_logs_booking_id"), "booking_activity_logs", ["booking_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_booking_activity_logs_booking_id"), table_name="booking_activity_logs")
    op.drop_table("booking_activity_logs")

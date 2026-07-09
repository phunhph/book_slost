"""add kol manual booking and progress fields

Revision ID: 20260709_0011
Revises: 20260709_0010
Create Date: 2026-07-09 14:50:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260709_0011"
down_revision = "20260709_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("source", sa.String(length=30), nullable=False, server_default="system"))
    op.add_column("bookings", sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("bookings", sa.Column("progress_note", sa.Text(), nullable=True))
    op.add_column("bookings", sa.Column("extension_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("bookings", sa.Column("extended_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("extension_note", sa.Text(), nullable=True))
    op.add_column("bookings", sa.Column("progress_updated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("bookings", "progress_updated_at")
    op.drop_column("bookings", "extension_note")
    op.drop_column("bookings", "extended_until")
    op.drop_column("bookings", "extension_count")
    op.drop_column("bookings", "progress_note")
    op.drop_column("bookings", "progress_percent")
    op.drop_column("bookings", "source")

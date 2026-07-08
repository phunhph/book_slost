"""add payment proof fields for bill review workflow

Revision ID: 20260708_0008
Revises: 20260708_0007
Create Date: 2026-07-08 21:05:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260708_0008"
down_revision = "20260708_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("payment_proof_url", sa.Text(), nullable=True))
    op.add_column(
        "bookings",
        sa.Column("payment_proof_note", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "bookings",
        sa.Column("payment_proof_uploaded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "bookings",
        sa.Column("payment_reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bookings", "payment_reviewed_at")
    op.drop_column("bookings", "payment_proof_uploaded_at")
    op.drop_column("bookings", "payment_proof_note")
    op.drop_column("bookings", "payment_proof_url")

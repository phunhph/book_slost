import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kol_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    guest_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    guest_zalo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guest_messenger: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pricing_type: Mapped[str] = mapped_column(String(30), default="match", nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="VND", nullable=False)
    payment_qr_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(30), default="unpaid", nullable=False)
    payment_proof_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_proof_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payment_proof_uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="system", nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    extension_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extended_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extension_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    kol = relationship("User", foreign_keys=[kol_user_id])
    customer = relationship("User", foreign_keys=[customer_user_id])
    activity_logs = relationship(
        "BookingActivityLog",
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="BookingActivityLog.created_at.desc()",
    )


class BookingActivityLog(Base):
    __tablename__ = "booking_activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    booking = relationship("Booking", back_populates="activity_logs")
    actor = relationship("User", foreign_keys=[actor_user_id])


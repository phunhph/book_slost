from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookingCreateRequest(BaseModel):
    kol_user_id: UUID
    scheduled_at: datetime
    pricing_type: str = Field(default="match", pattern="^(match|hourly)$")
    quantity: int = Field(default=1, ge=1, le=100)
    notes: str | None = Field(default=None, max_length=2000)
    guest_name: str | None = Field(default=None, max_length=150)
    guest_phone: str | None = Field(default=None, max_length=30)
    guest_zalo: str | None = Field(default=None, max_length=100)
    guest_messenger: str | None = Field(default=None, max_length=100)


class KolManualBookingCreateRequest(BaseModel):
    scheduled_at: datetime
    pricing_type: str = Field(default="match", pattern="^(match|hourly)$")
    quantity: int = Field(default=1, ge=1, le=100)
    guest_name: str = Field(min_length=2, max_length=150)
    guest_phone: str | None = Field(default=None, max_length=30)
    guest_zalo: str | None = Field(default=None, max_length=100)
    guest_messenger: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)
    source: str = Field(default="manual", pattern="^(manual|external)$")


class BookingStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|completed|cancelled)$")


class PaymentReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    note: str | None = Field(default=None, max_length=500)


class BookingProgressUpdateRequest(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
    progress_note: str | None = Field(default=None, max_length=2000)
    extended_until: datetime | None = None
    extension_note: str | None = Field(default=None, max_length=2000)


class KolPublicCard(BaseModel):
    user_id: UUID
    username: str | None
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    primary_color: str | None = None
    pricing_type: str | None = None
    price_per_match: int | None = None
    price_per_hour: int | None = None
    currency: str | None = None
    has_bank_account: bool = False


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kol_user_id: UUID
    customer_user_id: UUID | None
    guest_name: str | None
    guest_phone: str | None
    guest_zalo: str | None
    guest_messenger: str | None
    scheduled_at: datetime
    pricing_type: str
    quantity: int
    unit_price: int
    total_amount: int
    currency: str
    payment_qr_url: str | None
    payment_code: str | None
    payment_status: str
    payment_proof_url: str | None = None
    payment_proof_note: str | None = None
    payment_proof_uploaded_at: datetime | None = None
    payment_reviewed_at: datetime | None = None
    source: str = "system"
    progress_percent: int = 0
    progress_note: str | None = None
    extension_count: int = 0
    extended_until: datetime | None = None
    extension_note: str | None = None
    progress_updated_at: datetime | None = None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    kol_display_name: str | None = None
    kol_username: str | None = None
    customer_email: str | None = None
    bank_name: str | None = None
    bank_account_number: str | None = None
    bank_account_name: str | None = None


class BookingActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID
    actor_user_id: UUID | None = None
    actor_role: str | None = None
    action: str
    message: str
    metadata: dict | None = None
    created_at: datetime


class RevenueSeries(BaseModel):
    labels: list[str]
    gross: list[int]
    collected: list[int]
    booking_counts: list[int]


class DashboardStatsResponse(BaseModel):
    total_bookings: int
    pending_bookings: int
    upcoming_bookings: int
    collected_revenue: int = 0
    unpaid_revenue: int = 0
    completed_bookings: int = 0
    confirmed_bookings: int = 0
    cancelled_bookings: int = 0
    proof_submitted_bookings: int = 0
    revenue_by_month: RevenueSeries

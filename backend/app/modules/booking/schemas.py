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


class BookingStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|completed|cancelled)$")


class PaymentReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    note: str | None = Field(default=None, max_length=500)


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

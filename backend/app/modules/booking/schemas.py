from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookingCreateRequest(BaseModel):
    kol_user_id: UUID
    scheduled_at: datetime
    notes: str | None = Field(default=None, max_length=2000)
    guest_name: str | None = Field(default=None, max_length=150)
    guest_phone: str | None = Field(default=None, max_length=30)
    guest_zalo: str | None = Field(default=None, max_length=100)
    guest_messenger: str | None = Field(default=None, max_length=100)


class BookingStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|completed|cancelled)$")


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
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    kol_display_name: str | None = None
    kol_username: str | None = None
    customer_email: str | None = None


class KolPublicCard(BaseModel):
    user_id: UUID
    username: str | None
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    primary_color: str | None = None

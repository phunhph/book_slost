import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


DEFAULT_LAYOUT = [
    {"id": "media_block", "active": True},
    {"id": "booking_block", "active": True},
    {"id": "products_block", "active": True},
    {"id": "affiliate_block", "active": True},
]


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    username: Mapped[str | None] = mapped_column(String(100), unique=True, index=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme_mode: Mapped[str] = mapped_column(String(50), default="light", nullable=False)
    font_family: Mapped[str] = mapped_column(String(100), default="Inter", nullable=False)
    primary_color: Mapped[str] = mapped_column(String(20), default="#FF007F", nullable=False)
    text_color: Mapped[str] = mapped_column(String(20), default="#111111", nullable=False)
    bg_type: Mapped[str] = mapped_column(String(50), default="color", nullable=False)
    bg_value: Mapped[str | None] = mapped_column(Text, default="#FFFFFF", nullable=True)
    avatar_style: Mapped[str] = mapped_column(String(50), default="circle", nullable=False)
    button_style: Mapped[str] = mapped_column(String(50), default="filled", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    zalo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    messenger: Mapped[str | None] = mapped_column(String(100), nullable=True)
    layout_structure: Mapped[list[dict]] = mapped_column(JSONB, default=lambda: DEFAULT_LAYOUT.copy(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="profile")

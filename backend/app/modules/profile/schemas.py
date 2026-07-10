from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_THEME_MODES = {"light", "dark", "custom"}
ALLOWED_BG_TYPES = {"color", "gradient", "image"}
ALLOWED_AVATAR_STYLES = {"circle", "square", "rounded"}
ALLOWED_BUTTON_STYLES = {"filled", "outline", "shadow"}
ALLOWED_PRICING_TYPES = {"match", "hourly"}


class UserProfileUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    bio: str | None = None
    avatar_url: str | None = None
    theme_mode: str | None = None
    font_family: str | None = Field(default=None, max_length=100)
    primary_color: str | None = Field(default=None, max_length=20)
    text_color: str | None = Field(default=None, max_length=20)
    bg_type: str | None = None
    bg_value: str | None = None
    avatar_style: str | None = None
    button_style: str | None = None
    phone: str | None = Field(default=None, max_length=30)
    zalo: str | None = Field(default=None, max_length=100)
    messenger: str | None = Field(default=None, max_length=100)
    pricing_type: str | None = None
    price_per_match: int | None = Field(default=None, ge=0)
    price_per_hour: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    bank_name: str | None = Field(default=None, max_length=100)
    bank_code: str | None = Field(default=None, max_length=20)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_account_name: str | None = Field(default=None, max_length=150)
    layout_structure: dict[str, Any] | None = None
    contact_links: list[dict] | None = None

    @field_validator("theme_mode")
    @classmethod
    def validate_theme_mode(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_THEME_MODES:
            raise ValueError("theme_mode must be one of: light, dark, custom")
        return value

    @field_validator("bg_type")
    @classmethod
    def validate_bg_type(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_BG_TYPES:
            raise ValueError("bg_type must be one of: color, gradient, image")
        return value

    @field_validator("avatar_style")
    @classmethod
    def validate_avatar_style(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_AVATAR_STYLES:
            raise ValueError("avatar_style must be one of: circle, square, rounded")
        return value

    @field_validator("button_style")
    @classmethod
    def validate_button_style(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_BUTTON_STYLES:
            raise ValueError("button_style must be one of: filled, outline, shadow")
        return value

    @field_validator("pricing_type")
    @classmethod
    def validate_pricing_type(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_PRICING_TYPES:
            raise ValueError("pricing_type phải là match hoặc hourly")
        return value


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str | None
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    theme_mode: str
    font_family: str
    primary_color: str
    text_color: str
    bg_type: str
    bg_value: str | None
    avatar_style: str
    button_style: str
    phone: str | None
    zalo: str | None
    messenger: str | None
    pricing_type: str
    price_per_match: int
    price_per_hour: int
    currency: str
    bank_name: str | None = None
    bank_code: str | None = None
    bank_account_number: str | None = None
    bank_account_name: str | None = None
    layout_structure: dict[str, Any]
    contact_links: list[dict] = []
    created_at: datetime
    updated_at: datetime


class SocialPlatformResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    label: str
    category: str
    is_active: bool
    icon: str | None = None
    created_at: datetime
    updated_at: datetime


class SocialPlatformCreateRequest(BaseModel):
    key: str = Field(min_length=2, max_length=50, pattern="^[a-z0-9_]+$")
    label: str = Field(min_length=2, max_length=100)
    category: str = Field(pattern="^(contact|social)$")
    is_active: bool = True
    icon: str | None = None


class SocialPlatformUpdateRequest(BaseModel):
    key: str | None = Field(default=None, min_length=2, max_length=50, pattern="^[a-z0-9_]+$")
    label: str | None = Field(default=None, min_length=2, max_length=100)
    category: str | None = Field(default=None, pattern="^(contact|social)$")
    is_active: bool | None = None
    icon: str | None = None

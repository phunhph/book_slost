from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_THEME_MODES = {"light", "dark", "custom"}
ALLOWED_BG_TYPES = {"color", "gradient", "image"}
ALLOWED_AVATAR_STYLES = {"circle", "square", "rounded"}
ALLOWED_BUTTON_STYLES = {"filled", "outline", "shadow"}
ALLOWED_BLOCK_IDS = {"media_block", "booking_block", "products_block", "affiliate_block"}


class LayoutBlock(BaseModel):
    id: str
    active: bool = True

    @field_validator("id")
    @classmethod
    def validate_block_id(cls, value: str) -> str:
        if value not in ALLOWED_BLOCK_IDS:
            raise ValueError(f"Unsupported block id: {value}")
        return value


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
    layout_structure: list[LayoutBlock] | None = None

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
    layout_structure: list[LayoutBlock]
    created_at: datetime
    updated_at: datetime

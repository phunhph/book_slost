from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterLocalRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    username: str | None = Field(default=None, min_length=3, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)


class LoginLocalRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(min_length=10)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    auth_provider: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    message: str = "Authenticated successfully."


class RegisterLocalResponse(AuthResponse):
    message: str = "User registered successfully."


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    display_name: str | None = None
    username: str | None = None
    phone: str | None = None
    contact_links: list[dict] = []
    social_links: list[dict] = []


class AdminUserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(admin|kol|customer)$")
    is_active: bool = True
    display_name: str | None = None
    phone: str | None = None
    username: str | None = None
    contact_links: list[dict] = []
    social_links: list[dict] = []


class AdminUserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str | None = Field(default=None, pattern="^(admin|kol|customer)$")
    is_active: bool | None = None
    display_name: str | None = None
    phone: str | None = None
    username: str | None = None
    contact_links: list[dict] | None = None
    social_links: list[dict] | None = None

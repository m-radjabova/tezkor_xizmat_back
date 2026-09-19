from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole
from app.schemas.common import ORMModel


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    password: str = Field(min_length=6, max_length=128)


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.CUSTOMER


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    role: UserRole | None = None
    is_blocked: bool | None = None
    organization_name: str | None = Field(default=None, min_length=2, max_length=150)
    responsible_person: str | None = Field(default=None, min_length=2, max_length=100)
    provider_category_ids: list[UUID] | None = None


class UserRead(ORMModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: str | None
    avatar_url: str | None
    is_blocked: bool
    role: UserRole
    organization_name: str | None
    responsible_person: str | None
    provider_category_ids: list[UUID]
    created_at: datetime
    updated_at: datetime


class UserListRead(BaseModel):
    items: list[UserRead]
    total: int
    limit: int
    offset: int
    active_count: int
    blocked_count: int

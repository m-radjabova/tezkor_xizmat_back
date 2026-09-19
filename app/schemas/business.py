from datetime import datetime, time
from uuid import UUID

from pydantic import Field

from app.schemas.category import CategoryRead
from app.schemas.common import ORMModel, SchemaModel


class BusinessBase(SchemaModel):
    category_id: UUID
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=3000)
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    logo_url: str | None = None
    address: str = Field(min_length=3, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    working_days: str | None = Field(default=None, min_length=2, max_length=100)
    open_time: time | None = None
    close_time: time | None = None
    images: list[str] = Field(default_factory=list)


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(SchemaModel):
    category_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=3000)
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    logo_url: str | None = None
    address: str | None = Field(default=None, min_length=3, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    working_days: str | None = Field(default=None, min_length=2, max_length=100)
    open_time: time | None = None
    close_time: time | None = None
    images: list[str] | None = None


class BusinessVerify(SchemaModel):
    is_verified: bool


class BusinessRead(ORMModel):
    id: UUID
    owner_id: UUID
    category_id: UUID
    name: str
    description: str | None
    phone: str | None
    logo_url: str | None
    address: str
    latitude: float
    longitude: float
    working_days: str | None
    open_time: time | None
    close_time: time | None
    images: list[str]
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryRead | None = None
    rating_average: float | None = None
    rating_count: int = 0


class BusinessListRead(SchemaModel):
    items: list[BusinessRead]
    total: int
    limit: int
    offset: int
    pending_count: int
    verified_count: int

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel, SchemaModel


class CategoryCreate(SchemaModel):
    name: str = Field(min_length=2, max_length=255)
    icon: str | None = Field(default=None, max_length=255)


class CategoryUpdate(SchemaModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    icon: str | None = Field(default=None, max_length=255)


class CategoryRead(ORMModel):
    id: UUID
    name: str
    icon: str | None
    created_at: datetime

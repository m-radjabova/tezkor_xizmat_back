from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel, SchemaModel
from app.schemas.business import BusinessRead
from app.schemas.user import UserRead


class ReviewCreate(SchemaModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class ReviewUpdate(SchemaModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class ReviewRead(ORMModel):
    id: UUID
    business_id: UUID
    user_id: UUID
    rating: int
    comment: str | None
    is_approved: bool
    created_at: datetime
    user: UserRead | None = None
    business: BusinessRead | None = None

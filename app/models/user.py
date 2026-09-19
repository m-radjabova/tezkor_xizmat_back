import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import UserRole, sql_enum


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    firebase_uid: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false", index=True)
    role: Mapped[UserRole] = mapped_column(
        sql_enum(UserRole, "user_role"),
        nullable=False,
        default=UserRole.CUSTOMER,
    )
    organization_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    responsible_person: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_category_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    businesses = relationship("Business", back_populates="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

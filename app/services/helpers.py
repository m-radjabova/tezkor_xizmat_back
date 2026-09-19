from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.user import User


def ensure_email_unique(db: Session, email: str, exclude_user_id: UUID | None = None) -> None:
    statement = select(User).where(User.email == email)
    if exclude_user_id:
        statement = statement.where(User.id != exclude_user_id)
    if db.scalar(statement):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")


def ensure_phone_unique(db: Session, phone: str | None, exclude_user_id: UUID | None = None) -> None:
    if not phone:
        return
    statement = select(User).where(User.phone == phone)
    if exclude_user_id:
        statement = statement.where(User.id != exclude_user_id)
    if db.scalar(statement):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already exists")


def get_category_or_404(db: Session, category_id: UUID) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def validate_category_ids(db: Session, category_ids: list[UUID]) -> list[str]:
    if not category_ids:
        return []
    unique_ids = list(dict.fromkeys(category_ids))
    found_ids = set(db.scalars(select(Category.id).where(Category.id.in_(unique_ids))).all())
    missing_ids = [str(category_id) for category_id in unique_ids if category_id not in found_ids]
    if missing_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categories not found: {', '.join(missing_ids)}")
    return [str(category_id) for category_id in unique_ids]


def validate_category(db: Session, category_id: UUID | None) -> Category | None:
    if category_id is None:
        return None
    return get_category_or_404(db, category_id)

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.imagekit import upload_category_logo_to_imagekit


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)).all())


def get_category_or_404(db: Session, category_id: UUID) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def create_category(db: Session, payload: CategoryCreate) -> Category:
    if db.scalar(select(Category).where(func.lower(Category.name) == payload.name.lower())):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, payload: CategoryUpdate) -> Category:
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] != category.name:
        if db.scalar(select(Category).where(func.lower(Category.name) == data["name"].lower(), Category.id != category.id)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    for field, value in data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    business_count = db.scalar(select(func.count()).select_from(Business).where(Business.category_id == category.id)) or 0
    if business_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category cannot be deleted while businesses use it",
        )
    db.delete(category)
    db.commit()


def upload_category_logo_file(file) -> str:
    return upload_category_logo_to_imagekit(file)

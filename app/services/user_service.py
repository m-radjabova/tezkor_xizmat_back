from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.helpers import ensure_email_unique, ensure_phone_unique, validate_category_ids
from app.utils.imagekit import upload_avatar_to_imagekit


def list_users(
    db: Session,
    role: UserRole | None = None,
    status_filter: str = "all",
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, object]:
    filters = []

    if role:
        filters.append(User.role == role)
    if status_filter == "active":
        filters.append(User.is_blocked.is_(False))
    elif status_filter == "blocked":
        filters.append(User.is_blocked.is_(True))
    if search:
        search_text = f"%{search}%"
        filters.append(
            or_(
                User.full_name.ilike(search_text),
                User.organization_name.ilike(search_text),
                User.responsible_person.ilike(search_text),
                User.email.ilike(search_text),
                User.phone.ilike(search_text),
            )
        )

    count_statement = select(func.count()).select_from(User)
    items_statement = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    active_count_statement = select(func.count()).select_from(User).where(User.is_blocked.is_(False))
    blocked_count_statement = select(func.count()).select_from(User).where(User.is_blocked.is_(True))

    if role:
        active_count_statement = active_count_statement.where(User.role == role)
        blocked_count_statement = blocked_count_statement.where(User.role == role)
    if filters:
        count_statement = count_statement.where(*filters)
        items_statement = items_statement.where(*filters)

    return {
        "items": list(db.scalars(items_statement).all()),
        "total": db.scalar(count_statement) or 0,
        "limit": limit,
        "offset": offset,
        "active_count": db.scalar(active_count_statement) or 0,
        "blocked_count": db.scalar(blocked_count_statement) or 0,
    }


def create_user(db: Session, payload: UserCreate) -> User:
    ensure_email_unique(db, payload.email)
    ensure_phone_unique(db, payload.phone)
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_or_404(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    if "email" in data:
        ensure_email_unique(db, data["email"], exclude_user_id=user.id)
    if "phone" in data:
        ensure_phone_unique(db, data["phone"], exclude_user_id=user.id)
    if "provider_category_ids" in data and data["provider_category_ids"] is not None:
        data["provider_category_ids"] = validate_category_ids(db, data["provider_category_ids"])

    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def upload_avatar(db: Session, user: User, file: UploadFile) -> User:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed")

    user.avatar_url = upload_avatar_to_imagekit(file)
    db.commit()
    db.refresh(user)
    return user


def delete_avatar(db: Session, user: User) -> User:
    user.avatar_url = None
    db.commit()
    db.refresh(user)
    return user

from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.business import Business
from app.models.category import Category
from app.models.enums import UserRole
from app.models.review import Review
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate
from app.services.helpers import validate_category
from app.utils.imagekit import upload_business_gallery_to_imagekit, upload_business_logo_to_imagekit


def _business_query():
    return select(Business).options(joinedload(Business.category))


def _attach_review_stats(db: Session, businesses: list[Business]) -> list[Business]:
    if not businesses:
        return businesses

    business_ids = [business.id for business in businesses]
    rows = db.execute(
        select(
            Review.business_id,
            func.avg(Review.rating).label("rating_average"),
            func.count(Review.id).label("rating_count"),
        )
        .where(
            Review.business_id.in_(business_ids),
            Review.is_approved.is_(True),
        )
        .group_by(Review.business_id)
    ).all()
    stats = {
        business_id: (float(rating_average), int(rating_count))
        for business_id, rating_average, rating_count in rows
    }

    for business in businesses:
        rating_average, rating_count = stats.get(business.id, (None, 0))
        business.rating_average = rating_average
        business.rating_count = rating_count

    return businesses


def list_public_businesses(
    db: Session,
    category_id: UUID | None = None,
    search: str | None = None,
    limit: int = 8,
    offset: int = 0,
    latitude: float | None = None,
    longitude: float | None = None,
    sort_by: str = "newest",
    min_rating: float | None = None,
) -> list[Business]:
    review_stats = (
        select(
            Review.business_id.label("business_id"),
            func.avg(Review.rating).label("rating_average"),
            func.count(Review.id).label("rating_count"),
        )
        .where(Review.is_approved.is_(True))
        .group_by(Review.business_id)
        .subquery()
    )

    statement = (
        _business_query()
        .outerjoin(review_stats, review_stats.c.business_id == Business.id)
        .where(Business.is_verified.is_(True))
    )
    if category_id:
        statement = statement.where(Business.category_id == category_id)
    if search:
        search_text = f"%{search}%"
        statement = statement.join(Category, Business.category_id == Category.id).where(
            or_(
                Business.name.ilike(search_text),
                Business.address.ilike(search_text),
                Business.description.ilike(search_text),
                Category.name.ilike(search_text),
            )
        )
    if min_rating is not None:
        statement = statement.where(func.coalesce(review_stats.c.rating_average, 0) >= min_rating)
    if sort_by == "distance" and latitude is not None and longitude is not None:
        distance = (Business.latitude - latitude) * (Business.latitude - latitude) + (
            Business.longitude - longitude
        ) * (Business.longitude - longitude)
        statement = statement.order_by(distance.asc(), Business.created_at.desc())
    elif sort_by == "rating":
        statement = statement.order_by(
            func.coalesce(review_stats.c.rating_average, 0).desc(),
            func.coalesce(review_stats.c.rating_count, 0).desc(),
            Business.created_at.desc(),
        )
    else:
        statement = statement.order_by(Business.created_at.desc())
    statement = statement.limit(limit).offset(offset)
    businesses = list(db.scalars(statement).unique().all())
    return _attach_review_stats(db, businesses)


def list_owner_businesses(db: Session, owner: User) -> list[Business]:
    return list(db.scalars(_business_query().where(Business.owner_id == owner.id).order_by(Business.created_at.desc())).unique().all())


def list_all_businesses(
    db: Session,
    search: str | None = None,
    status_filter: str = "all",
    limit: int = 10,
    offset: int = 0,
) -> dict[str, object]:
    filters = []
    if status_filter == "verified":
        filters.append(Business.is_verified.is_(True))
    elif status_filter == "pending":
        filters.append(Business.is_verified.is_(False))
    if search:
        search_text = f"%{search}%"
        filters.append(or_(Business.name.ilike(search_text), Business.address.ilike(search_text)))

    count_statement = select(func.count()).select_from(Business)
    items_statement = _business_query().order_by(Business.created_at.desc()).limit(limit).offset(offset)
    if filters:
        count_statement = count_statement.where(*filters)
        items_statement = items_statement.where(*filters)

    total = db.scalar(count_statement) or 0
    pending_count = db.scalar(select(func.count()).select_from(Business).where(Business.is_verified.is_(False))) or 0
    verified_count = db.scalar(select(func.count()).select_from(Business).where(Business.is_verified.is_(True))) or 0
    items = list(db.scalars(items_statement).unique().all())

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "pending_count": pending_count,
        "verified_count": verified_count,
    }


def get_business_or_404(db: Session, business_id: UUID) -> Business:
    business = db.scalar(_business_query().where(Business.id == business_id))
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


def get_public_business_or_404(db: Session, business_id: UUID) -> Business:
    business = db.scalar(_business_query().where(Business.id == business_id, Business.is_verified.is_(True)))
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return _attach_review_stats(db, [business])[0]


def ensure_owner_or_admin(business: Business, current_user: User) -> None:
    if current_user.role == UserRole.ADMIN:
        return
    if business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can manage only your businesses")


def create_business(db: Session, owner: User, payload: BusinessCreate) -> Business:
    validate_category(db, payload.category_id)
    business = Business(owner_id=owner.id, **payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return get_business_or_404(db, business.id)


def create_business_with_uploads(
    db: Session,
    owner: User,
    payload: BusinessCreate,
    logo: UploadFile | None = None,
    gallery: list[UploadFile] | None = None,
) -> Business:
    validate_category(db, payload.category_id)
    data = payload.model_dump()
    if logo:
        validate_image_file(logo)
        data["logo_url"] = upload_business_logo_to_imagekit(logo)
    if gallery:
        data["images"] = upload_gallery_files(gallery)
    business = Business(owner_id=owner.id, **data)
    db.add(business)
    db.commit()
    db.refresh(business)
    return get_business_or_404(db, business.id)


def update_business(db: Session, business: Business, payload: BusinessUpdate) -> Business:
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"]:
        validate_category(db, data["category_id"])
    for field, value in data.items():
        setattr(business, field, value)
    db.commit()
    db.refresh(business)
    return get_business_or_404(db, business.id)


def set_business_verification(db: Session, business: Business, is_verified: bool) -> Business:
    business.is_verified = is_verified
    db.commit()
    db.refresh(business)
    return get_business_or_404(db, business.id)


def delete_business(db: Session, business: Business) -> None:
    db.delete(business)
    db.commit()


def validate_image_file(file: UploadFile) -> None:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed")


def upload_gallery_files(files: list[UploadFile]) -> list[str]:
    if not files:
        return []
    urls = []
    for file in files:
        validate_image_file(file)
        urls.append(upload_business_gallery_to_imagekit(file))
    return urls


def upload_business_logo_file(file: UploadFile) -> str:
    validate_image_file(file)
    return upload_business_logo_to_imagekit(file)


def upload_business_logo(db: Session, business: Business, file: UploadFile) -> Business:
    validate_image_file(file)
    business.logo_url = upload_business_logo_to_imagekit(file)
    db.commit()
    db.refresh(business)
    return get_business_or_404(db, business.id)


def upload_business_gallery_images(db: Session, business: Business, files: list[UploadFile]) -> Business:
    images = list(business.images or [])
    images.extend(upload_gallery_files(files))
    business.images = images
    db.commit()
    db.refresh(business)
    return get_business_or_404(db, business.id)

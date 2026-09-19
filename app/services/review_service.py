from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.business import Business
from app.models.enums import UserRole
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate


def list_business_reviews(db: Session, business_id: UUID) -> list[Review]:
    return list(
        db.scalars(
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.business_id == business_id, Review.is_approved.is_(True))
            .order_by(Review.created_at.desc())
        )
        .unique()
        .all()
    )


def list_featured_reviews(db: Session, limit: int = 3) -> list[Review]:
    return list(
        db.scalars(
            select(Review)
            .join(Business, Review.business_id == Business.id)
            .options(joinedload(Review.user), joinedload(Review.business).joinedload(Business.category))
            .where(
                Review.is_approved.is_(True),
                Review.rating == 5,
                Business.is_verified.is_(True),
            )
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        .unique()
        .all()
    )


def get_review_or_404(db: Session, review_id: UUID) -> Review:
    review = db.scalar(
        select(Review)
        .options(joinedload(Review.user), joinedload(Review.business))
        .where(Review.id == review_id)
    )
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


def list_provider_reviews(db: Session, provider: User, status_filter: str = "all") -> list[Review]:
    statement = (
        select(Review)
        .join(Business, Review.business_id == Business.id)
        .options(joinedload(Review.user), joinedload(Review.business).joinedload(Business.category))
        .where(Business.owner_id == provider.id)
        .order_by(Review.created_at.desc())
    )

    if status_filter == "approved":
        statement = statement.where(Review.is_approved.is_(True))
    elif status_filter == "pending":
        statement = statement.where(Review.is_approved.is_(False))

    return list(
        db.scalars(statement)
        .unique()
        .all()
    )


def create_review(db: Session, business_id: UUID, user: User, payload: ReviewCreate) -> Review:
    if not db.get(Business, business_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    existing = db.scalar(select(Review).where(Review.business_id == business_id, Review.user_id == user.id))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already reviewed this business")
    review = Review(business_id=business_id, user_id=user.id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return get_review_or_404(db, review.id)


def ensure_review_business_owner_or_admin(review: Review, user: User) -> None:
    if user.role == UserRole.ADMIN:
        return
    if not review.business or review.business.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can manage only your business reviews")


def approve_review(db: Session, review: Review, user: User) -> Review:
    ensure_review_business_owner_or_admin(review, user)
    review.is_approved = True
    db.commit()
    db.refresh(review)
    return get_review_or_404(db, review.id)


def reject_review(db: Session, review: Review, user: User) -> None:
    ensure_review_business_owner_or_admin(review, user)
    db.delete(review)
    db.commit()


def update_review(db: Session, review: Review, user: User, payload: ReviewUpdate) -> Review:
    if user.role != UserRole.ADMIN and review.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can update only your review")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    return get_review_or_404(db, review.id)


def delete_review(db: Session, review: Review, user: User) -> None:
    if user.role != UserRole.ADMIN and review.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can delete only your review")
    db.delete(review)
    db.commit()

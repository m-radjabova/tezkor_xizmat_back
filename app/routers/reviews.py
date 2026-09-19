from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_customer, require_provider
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review_service import (
    approve_review,
    create_review,
    delete_review,
    get_review_or_404,
    list_business_reviews,
    list_featured_reviews,
    list_provider_reviews,
    reject_review,
    update_review,
)

business_reviews_router = APIRouter(prefix="/businesses/{id}/reviews", tags=["Reviews"])
reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])


@business_reviews_router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def add_review(
    id: UUID,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    return create_review(db, id, current_user, payload)


@business_reviews_router.get("", response_model=list[ReviewRead])
def get_reviews(id: UUID, db: Session = Depends(get_db)):
    return list_business_reviews(db, id)


@reviews_router.get("/featured", response_model=list[ReviewRead])
def get_featured_reviews(limit: int = 3, db: Session = Depends(get_db)):
    return list_featured_reviews(db, min(max(limit, 1), 12))


@reviews_router.get("/provider/my", response_model=list[ReviewRead])
def get_my_business_reviews(
    status_filter: str = Query(default="all", pattern="^(all|approved|pending)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider),
):
    return list_provider_reviews(db, current_user, status_filter)


@reviews_router.patch("/{id}", response_model=ReviewRead)
def edit_review(
    id: UUID,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_review_or_404(db, id)
    return update_review(db, review, current_user, payload)


@reviews_router.patch("/{id}/approve", response_model=ReviewRead)
def approve_my_business_review(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_review_or_404(db, id)
    return approve_review(db, review, current_user)


@reviews_router.delete("/{id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_my_business_review(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_review_or_404(db, id)
    reject_review(db, review, current_user)


@reviews_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_review_or_404(db, id)
    delete_review(db, review, current_user)

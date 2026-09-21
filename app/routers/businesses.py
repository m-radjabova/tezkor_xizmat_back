from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin, require_provider
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessListRead, BusinessRead, BusinessUpdate
from app.services.business_service import (
    create_business,
    delete_business,
    ensure_owner_or_admin,
    get_public_business_or_404,
    get_business_or_404,
    list_all_businesses,
    list_owner_businesses,
    list_public_businesses,
    set_business_verification,
    update_business,
)

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.post("", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
def create_my_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider),
):
    return create_business(db, current_user, payload)


@router.get("", response_model=list[BusinessRead])
def get_public_businesses(
    category_id: UUID | None = None,
    search: str | None = Query(default=None, min_length=2, max_length=100),
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    sort_by: str = Query(default="newest", pattern="^(newest|distance|rating)$"),
    min_rating: float | None = Query(default=None, ge=1, le=5),
    limit: int = Query(default=8, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return list_public_businesses(db, category_id, search, limit, offset, latitude, longitude, sort_by, min_rating)


@router.get("/my", response_model=list[BusinessRead])
def get_my_businesses(db: Session = Depends(get_db), current_user: User = Depends(require_provider)):
    return list_owner_businesses(db, current_user)


@router.get("/admin/all", response_model=BusinessListRead, dependencies=[Depends(require_admin)])
def get_all_businesses_for_admin(
    search: str | None = Query(default=None, min_length=2, max_length=100),
    status_filter: str = Query(default="all", pattern="^(all|pending|verified)$"),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return list_all_businesses(db, search, status_filter, limit, offset)


@router.get("/{id}", response_model=BusinessRead)
def get_business(id: UUID, db: Session = Depends(get_db)):
    return get_public_business_or_404(db, id)


@router.patch("/{id}/verify", response_model=BusinessRead)
def verify_business_by_admin(
    id: UUID,
    payload: dict[str, bool],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    business = get_business_or_404(db, id)
    return set_business_verification(db, business, bool(payload.get("is_verified", False)))


@router.patch("/{id}", response_model=BusinessRead)
def update_my_business(
    id: UUID,
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_business_or_404(db, id)
    ensure_owner_or_admin(business, current_user)
    return update_business(db, business, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_business(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_business_or_404(db, id)
    ensure_owner_or_admin(business, current_user)
    delete_business(db, business)

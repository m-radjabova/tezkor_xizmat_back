from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.roles import require_admin
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import (
    create_category,
    delete_category,
    get_category_or_404,
    list_categories,
    update_category,
    upload_category_logo_file,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def get_categories(db: Session = Depends(get_db)):
    return list_categories(db)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_new_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, payload)


@router.patch("/{id}", response_model=CategoryRead, dependencies=[Depends(require_admin)])
def update_existing_category(id: UUID, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = get_category_or_404(db, id)
    return update_category(db, category, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_existing_category(id: UUID, db: Session = Depends(get_db)):
    category = get_category_or_404(db, id)
    delete_category(db, category)


@router.post("/logo", dependencies=[Depends(require_admin)])
def upload_category_logo(file: UploadFile = File(...)):
    return {"url": upload_category_logo_file(file)}

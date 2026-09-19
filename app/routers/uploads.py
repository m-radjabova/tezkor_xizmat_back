from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies.roles import require_provider
from app.services.business_service import upload_business_logo_file, upload_gallery_files

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/images")
def upload_images(
    files: list[UploadFile] = File(...),
    _=Depends(require_provider),
):
    return {"urls": upload_gallery_files(files)}


@router.post("/business-logo")
def upload_business_logo_image(
    file: UploadFile = File(...),
    _=Depends(require_provider),
):
    return {"url": upload_business_logo_file(file)}

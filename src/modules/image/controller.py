from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service

router = APIRouter(prefix="/image", tags=["Image"])

@router.get("", response_model=list[schema.ImageOut])
def list_images(db: Session = Depends(get_db)):
    return service.list_images(db)

@router.get("/{image_id}", response_model=schema.ImageOut)
def get_image(image_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.get_image_or_404(db, image_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/upload", response_model=schema.ImageOut)
async def upload_image(
    post_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await service.create_image_from_upload(db, post_id, file)

@router.delete("/{image_id}", response_model=schema.ImageOut)
def delete_image(image_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.delete_image(db, image_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

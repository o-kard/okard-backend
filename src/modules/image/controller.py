from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from fastapi import Form

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
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    post_id: UUID | None = Form(None),
    clerk_id: str | None = Form(None),
):
    print(f"Received upload request: post_id={post_id}, user_id={clerk_id}, file={file.filename}")
    return await service.create_image_from_upload(db, file, post_id, clerk_id)

@router.delete("/{image_id}", response_model=schema.ImageOut)
def delete_image(image_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.delete_image(db, image_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

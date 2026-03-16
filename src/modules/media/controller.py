from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from fastapi import Form

router = APIRouter(prefix="/media", tags=["Media"])

@router.get("", response_model=list[schema.MediaOut])
def list_media(db: Session = Depends(get_db)):
    return service.list_media(db)

@router.get("/{media_id}", response_model=schema.MediaOut)
def get_media(media_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.get_media_or_404(db, media_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/upload", response_model=schema.MediaOut)
async def upload_media(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    campaign_id: UUID | None = Form(None),
    clerk_id: str | None = Form(None),
):
    print(f"Received upload request: campaign_id={campaign_id}, user_id={clerk_id}, file={file.filename}")
    return await service.create_media_from_upload(db, file, campaign_id, clerk_id)

@router.delete("/{media_id}", response_model=schema.MediaOut)
def delete_media(media_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.delete_media(db, media_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

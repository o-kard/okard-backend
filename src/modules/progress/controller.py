from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional, Union
import json
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from src.modules.common.file_utils import validate_image_size

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.get("", response_model=list[schema.ProgressOut])
def list_progress(campaign_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    return service.list_progress(db, campaign_id)

@router.get("/{progress_id}", response_model=schema.ProgressOut)
def get_progress(progress_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.get_progress(db, progress_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("", response_model=schema.ProgressOut)
async def create_progress(
    progress_data: str = Form(...),
    images: Union[List[UploadFile], UploadFile, None] = File(None),
    db: Session = Depends(get_db)
):
    try:
        data = schema.ProgressCreate(**json.loads(progress_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid progress_data")

    files_list = []
    if images:
        files_list = images if isinstance(images, list) else [images]
        for f in files_list:
            validate_image_size(f)

    return await service.create_progress_with_images(db, data, files_list)

@router.put("/{progress_id}", response_model=schema.ProgressOut)
async def update_progress(
    progress_id: UUID,
    progress_data: str = Form(...),
    images: Union[List[UploadFile], UploadFile, None] = File(None),
    db: Session = Depends(get_db)
):
    try:
        data = schema.ProgressUpdate(**json.loads(progress_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid progress_data")

    files_list = None
    if images:
        files_list = images if isinstance(images, list) else [images]
        for f in files_list:
            validate_image_size(f)
    
    try:
        return await service.update_progress_with_images(db, progress_id, data, files_list)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{progress_id}")
def delete_progress(progress_id: UUID, db: Session = Depends(get_db)):
    try:
        service.delete_progress(db, progress_id)
        return {"OK": True}
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

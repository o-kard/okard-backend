import os
from typing import List, Optional
import uuid
from fastapi import  UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.media import model as media_model, repo as media_repo, service as media_service
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads" / "media"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _abs(rel: str) -> str:
   return (BASE_DIR / rel.lstrip("/")).as_posix()

def list_progress(db: Session, post_id: UUID | None = None):
    return repo.list_progress(db, post_id)

def get_progress(db: Session, progress_id: UUID):
    progress = repo.get_progress(db, progress_id)
    if not progress:
        raise ValueError("Progress not found")
    return progress

def update_progress(db: Session, progress_id: UUID, progress_data: schema.ProgressUpdate):
    db_progress = get_progress(db, progress_id)
    return repo.update_progress(db, db_progress, progress_data)

async def create_progress_with_images(
    db: Session,
    progress_data: schema.ProgressCreate,
    files: Optional[List[UploadFile]] = None
):
    # progress_data is a single object here, unlike campaign which was a list
    db_progress = repo.create_progress(db, progress_data)
    
    if files:
        await media_service._save_files_and_create_media(
            db,
            parent_type="progress",
            parent_id=db_progress.id,
            files=files,
            media_manifest=None,
        )
    return db_progress

async def update_progress_with_images(db: Session, progress_id: UUID,
                                      progress_data: schema.ProgressUpdate,
                                      files: Optional[List[UploadFile]] = None):
    db_progress = get_progress(db, progress_id)

    repo.update_progress(db, db_progress, progress_data)

    if files:
        for media in list(db_progress.media):
            if media.path:
                ap = _abs(media.path)
                if os.path.exists(ap):
                    os.remove(ap)
            media_repo.delete_media(db, media)
        db.commit()

        await media_service._save_files_and_create_media(
            db,
            parent_type="progress",
            parent_id=db_progress.id,
            files=files,
            media_manifest=None
        )

    return db_progress

def delete_progress(db: Session, progress_id: UUID):
    db_progress = get_progress(db, progress_id)
    
    for media in list(db_progress.media):
        if media.path:
            ap = _abs(media.path)
            if os.path.exists(ap):
                os.remove(ap)
        media_repo.delete_media(db, media)

    return repo.delete_progress(db, db_progress)

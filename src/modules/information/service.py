import os
from typing import List, Optional
import uuid
from fastapi import  UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.media import model as media_model, repo as media_repo, service as media_service
from pathlib import Path
import os
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "media"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _abs(rel: str) -> str:
   return (BASE_DIR / rel.lstrip("/")).as_posix()

def list_informations(db: Session):
    return repo.list_informations(db)

def get_information(db: Session, information_id: UUID):
    information = repo.get_information(db, information_id)
    if not information:
        raise ValueError("Information not found")
    return information

def update_information(db: Session, information_id: UUID, information_data: schema.InformationUpdate):
    db_information = get_information(db, information_id)
    return repo.update_information(db, db_information, information_data)


async def create_information_with_media(
    db: Session,
    information_data: List[schema.InformationCreate],
    files: List[UploadFile]
):
    db_informations = []
    for data in information_data:
        db_information = repo.create_information(db, data)
        await media_service._save_files_and_create_media(
            db,
            parent_type="information",
            parent_id=db_information.id,
            files=files,                       
            media_manifest=None,             
        )
        db_informations.append(db_information)
    return db_informations


async def update_information_with_media(db: Session, information_id: UUID,
                                      information_data: schema.InformationUpdate,
                                      files: Optional[List[UploadFile]] = None):
    db_information = get_information(db, information_id)

    repo.update_information(db, db_information, information_data)

    if not files:
        return db_information

    for media in list(db_information.media):
        if media.path:
            ap = _abs(media.path)
            if os.path.exists(ap):
                os.remove(ap)
        media_repo.delete_media(db, media)
    db.commit()

    await media_service._save_files_and_create_media(
        db,
        parent_type="information",
        parent_id=db_information.id,
        files=files,
        media_manifest=None
    )

    return db_information



def delete_information(db: Session, information_id: UUID):
    db_information = get_information(db, information_id)
    
    for media in list(db_information.media):
        if media.path:
            ap = _abs(media.path)
            if os.path.exists(ap):
                os.remove(ap)
        media_repo.delete_media(db, media)

    return repo.delete_information(db, db_information)

import os
from pathlib import Path
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from . import model, repo
from fastapi import UploadFile
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def create_image_from_upload(db: Session, post_id: UUID, file: UploadFile):
    content = await file.read()
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_name = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as f:
        f.write(content)

    db_image = model.Image(
        id=uuid4(),
        post_id=post_id,
        orig_name=file.filename,
        media_type=file.content_type,
        file_size=len(content),
        path=file_path.as_posix(), 
    )
    return repo.create_image(db, db_image)

def list_images(db: Session):
    return repo.list_images(db)

def get_image_or_404(db: Session, image_id: UUID):
    image = repo.get_image(db, image_id)
    if not image:
        raise ValueError("Image not found")
    return image

def delete_image(db: Session, image_id: UUID):
    db_image = get_image_or_404(db, image_id)
    return repo.delete_image(db, db_image)

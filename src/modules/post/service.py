import os
from typing import List
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.image import model as image_model, repo as image_repo
from pathlib import Path
from src.modules.user.repo import get_user_by_clerk_id 
import os
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def list_posts(db: Session):
    print(UPLOAD_DIR)
    return repo.list_posts(db)

def get_post(db: Session, post_id: UUID):
    post = repo.get_post(db, post_id)
    if not post:
        raise ValueError("Post not found")
    return post

def create_post(db: Session, post: schema.PostCreate):
    return repo.create_post(db, post)

def update_post(db: Session, post_id: UUID, post_data: schema.PostUpdate):
    db_post = get_post(db, post_id)
    return repo.update_post(db, db_post, post_data)

def delete_post(db: Session, post_id: UUID):
    db_post = get_post(db, post_id)

    for image in db_post.images:
        if image.path and os.path.exists(image.path):
            os.remove(image.path)

    return repo.delete_post(db, db_post)


async def create_post_by_clerk_id_with_images(
    db: Session,
    post_data: schema.PostCreate,
    clerk_id: str,
    files: List[UploadFile]
):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise ValueError("User not found")

    db_post = model.Post(**post_data.model_dump(), user_id=user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    for file in files:
        content = await file.read()
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / file_name

        with open(file_path, "wb") as f:
            f.write(content)

        image = image_model.Image(
            id=uuid.uuid4(),
            post_id=db_post.id,
            orig_name=file.filename,
            media_type=file.content_type,
            file_size=len(content),
            # path=file_path.as_posix(),
            path=f"/uploads/images/{file_name}"
        )
        image_repo.create_image(db, image)

    return db_post


async def update_post_with_images(db: Session, post_id: UUID, post_data: schema.PostUpdate, files: List[UploadFile]):
    db_post = get_post(db, post_id)
    
    for image in db_post.images:
        if image.path and os.path.exists(image.path):
            os.remove(image.path)
        db.delete(image)
    db.commit()

    repo.update_post(db, db_post, post_data)

    for file in files:
        content = await file.read()
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / file_name


        with open(file_path, "wb") as f:
            f.write(content)

        image = image_model.Image(
            id=uuid.uuid4(),
            post_id=db_post.id,
            orig_name=file.filename,
            media_type=file.content_type,
            file_size=len(content),
            # path=file_path.as_posix(),
            path=f"/uploads/images/{file_name}" 
        )
        image_repo.create_image(db, image)

    return db_post

def verify_post_owner(db: Session, post_id: UUID, clerk_id: str):
    user = get_user_by_clerk_id(db, clerk_id)
    post = get_post(db, post_id)
    if not user or post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    return post

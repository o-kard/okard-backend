from http.client import HTTPException
import os
from pathlib import Path
from typing import List
import uuid
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from src.modules.user.service import get_user_by_clerk_id
from . import model, repo
from fastapi import UploadFile
from typing import Optional
from src.modules.common.enums import ReferenceType

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def create_image_from_upload(
    db: Session, 
    file: UploadFile,
    post_id: Optional[UUID] = None,
    clerk_id: Optional[str] = None,
):
    ref_id = None
    ref_type = None

    if clerk_id:
        user = await get_user_by_clerk_id(db, clerk_id)
        if not user:
            raise HTTPException(404, "User not found")
        user_id = user.id
        print(f"User found: {user_id}")
        
        # Check existing image via handler
        # Assuming user has 'image' relationship working
        if user.image:
           old_path = user.image.path
           if old_path:
               abs_old_path = BASE_DIR / old_path.lstrip("/")
               try:
                   if abs_old_path.exists():
                       abs_old_path.unlink()
               except Exception:
                   pass
           # We need to delete the Image object. Cascade should handle handler?
           # If cascade is not set on handler FK, we might need to delete handler manually or rely on image deletion cascading to handler?
           # ImageHandler has FK to Image. If we delete Image, handler should be deleted?
           # Wait, check DB definition: creating FK... ondelete is default (No Action).
           # So deleting Image might fail if Handler exists! 
           # We should delete handler first or Image.
           # Actually, usually getting the image object and deleting it requires cleaning dependencies.
           repo.delete_image(db, user.image)

        ref_id = user.id
        ref_type = ReferenceType.user
            
    elif post_id:
        ref_id = post_id
        ref_type = ReferenceType.post
    else:
        raise ValueError("Either post_id or user_id is required")
    
    content = await file.read()
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_name = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as f:
        f.write(content)

    img_id = uuid4()
    db_image = model.Image(
        id=img_id,
        orig_name=file.filename,
        media_type=file.content_type,
        file_size=len(content),
        path=f"/uploads/images/{file_name}",
        display_order=0 
    )
    repo.create_image(db, db_image)

    # Create handler
    handler = model.ImageHandler(
        image_id=img_id,
        reference_id=ref_id,
        type=ref_type
    )
    db.add(handler)
    db.commit()

    return db_image

async def list_images(db: Session):
    return repo.list_images(db)

async def get_image_or_404(db: Session, image_id: UUID):
    image = repo.get_image(db, image_id)
    if not image:
        raise ValueError("Image not found")
    return image

async def delete_image(db: Session, image_id: UUID):
    db_image = await get_image_or_404(db, image_id)
    return repo.delete_image(db, db_image)

async def _save_files_and_create_images(
    db: Session,
    parent_type: str,          
    parent_id: UUID,
    files: List[UploadFile],
    images_manifest: Optional[List[dict]] = None,  
    start_index: int = 1,                           
):
    saved_images = []

    order_map: dict[str, int] = {}
    if images_manifest:
        for it in images_manifest:
            fn = (it.get("filename") or "").strip()
            if fn:
                order_map[fn] = int(it.get("display_order") or start_index)

    for i, file in enumerate(files, start=start_index):
        content = await file.read()
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / file_name

        with open(file_path, "wb") as f:
            f.write(content)

        img_order = order_map.get(file.filename, i)
        img_id = uuid4()

        image_kwargs = dict(
            id=img_id,
            orig_name=file.filename,
            media_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            path=f"/uploads/images/{file_name}",
            display_order=img_order,  
        )

        ref_type = None
        if parent_type == "reward":
            ref_type = ReferenceType.reward
        elif parent_type == "post":
            ref_type = ReferenceType.post
        elif parent_type == "campaign":
            ref_type = ReferenceType.campaign
        elif parent_type == "progress":
            ref_type = ReferenceType.progress
        elif parent_type == "report":
            ref_type = ReferenceType.report
        else:
            raise ValueError(f"Unknown parent_type: {parent_type}")

        image = model.Image(**image_kwargs)
        repo.create_image(db, image)

        handler = model.ImageHandler(
            image_id=img_id,
            reference_id=parent_id,
            type=ref_type
        )
        db.add(handler)
        
        saved_images.append(image)
    
    db.commit()
    return saved_images

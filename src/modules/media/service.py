from fastapi import HTTPException, UploadFile
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

UPLOAD_DIR = BASE_DIR / "uploads" / "media"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def create_media_from_upload(
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
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user.id
        print(f"User found: {user_id}")
        
        # Check existing media via handler
        if user.media:
           old_path = user.media.path
           if old_path:
               abs_old_path = BASE_DIR / old_path.lstrip("/")
               try:
                   if abs_old_path.exists():
                       abs_old_path.unlink()
               except Exception:
                   pass
           repo.delete_media(db, user.media)

        ref_id = user.id
        ref_type = ReferenceType.user
            
    elif post_id:
        ref_id = post_id
        ref_type = ReferenceType.post
    else:
        raise ValueError("Either post_id or user_id is required")
    
    content = await file.read()
    
    is_video = file.content_type and file.content_type.startswith("video/")
    max_size = 50 * 1024 * 1024 if is_video else 5 * 1024 * 1024
    limit_label = "50MB" if is_video else "5MB"

    if len(content) > max_size:
        raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds {limit_label} limit")
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/quicktime", "video/webm"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type for {file.filename}. Allowed: jpg, png, gif, webp, mp4, mov, webm")

    ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_name = f"{uuid4().hex}{ext}"
    
    # Create sub-directory based on reference type and ID
    sub_dir = UPLOAD_DIR / ref_type.value / str(ref_id)
    sub_dir.mkdir(parents=True, exist_ok=True)
    file_path = sub_dir / file_name

    with open(file_path, "wb") as f:
        f.write(content)

    media_id = uuid4()
    db_media = model.Media(
        id=media_id,
        orig_name=file.filename,
        media_type=file.content_type,
        file_size=len(content),
        path=f"/uploads/media/{ref_type.value}/{ref_id}/{file_name}",
        display_order=0 
    )
    repo.create_media(db, db_media)

    # Create handler
    handler = model.MediaHandler(
        media_id=media_id,
        reference_id=ref_id,
        type=ref_type
    )
    db.add(handler)
    db.commit()

    return db_media

def list_media(db: Session):
    return repo.list_media(db)

def get_media_or_404(db: Session, media_id: UUID):
    media = repo.get_media(db, media_id)
    if not media:
        raise ValueError("Media not found")
    return media

def delete_media(db: Session, media_id: UUID):
    db_media = get_media_or_404(db, media_id)
    return repo.delete_media(db, db_media)

async def _save_files_and_create_media(
    db: Session,
    parent_type: str,          
    parent_id: UUID,
    files: List[UploadFile],
    media_manifest: Optional[List[dict]] = None,  
    start_index: int = 1,                           
):
    saved_media = []

    order_map: dict[str, int] = {}
    if media_manifest:
        for it in media_manifest:
            fn = (it.get("filename") or "").strip()
            if fn:
                order_map[fn] = int(it.get("display_order") or start_index)

    for i, file in enumerate(files, start=start_index):
        content = await file.read()
        
        is_video = file.content_type and file.content_type.startswith("video/")
        max_size = 50 * 1024 * 1024 if is_video else 5 * 1024 * 1024
        limit_label = "50MB" if is_video else "5MB"

        if len(content) > max_size:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds {limit_label} limit")
        
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/quicktime", "video/webm"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type for {file.filename}. Allowed: jpg, png, gif, webp, mp4, mov, webm")

        ext = os.path.splitext(file.filename)[1] or ".jpg"
        file_name = f"{uuid4().hex}{ext}"
        
        # Create sub-directory based on reference type and ID
        sub_dir = UPLOAD_DIR / parent_type / str(parent_id)
        sub_dir.mkdir(parents=True, exist_ok=True)
        file_path = sub_dir / file_name

        with open(file_path, "wb") as f:
            f.write(content)

        img_order = order_map.get(file.filename, i)
        media_id = uuid4()

        media_kwargs = dict(
            id=media_id,
            orig_name=file.filename,
            media_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            path=f"/uploads/media/{parent_type}/{parent_id}/{file_name}",
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

        media = model.Media(**media_kwargs)
        repo.create_media(db, media)

        handler = model.MediaHandler(
            media_id=media_id,
            reference_id=parent_id,
            type=ref_type
        )
        db.add(handler)
        
        saved_media.append(media)
    
    db.commit()
    return saved_media

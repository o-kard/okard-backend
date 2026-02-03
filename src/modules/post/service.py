from datetime import datetime
import os
from typing import List, Optional
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy import Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.media import model as media_model, repo as media_repo, service as media_service
from src.modules.campaign import schema as campaign_schema, service as campaign_service
from src.modules.reward import schema as reward_schema, service as reward_service
from src.modules.model import service as model_service, schema as model_schema, repo as model_repo
from src.modules.country import service as country_service
from pathlib import Path
from src.modules.user.service import get_user_by_clerk_id 
import os
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "media"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def format_datetime(dt):
    if not dt:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat(timespec="minutes")
    return str(dt)

def _abs(rel: str) -> str:
    return (BASE_DIR / rel.lstrip("/")).as_posix()

# def _ensure_upload_dir():
#     UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# async def _save_images_and_attach_to_post(db: Session, db_post: model.Post, files: Optional[List[UploadFile]]):
#     if not files:
#         return
#     _ensure_upload_dir()
#     for file in files:
#         content = await file.read()
#         ext = os.path.splitext(file.filename)[1]
#         file_name = f"{uuid.uuid4().hex}{ext}"
#         (UPLOAD_DIR / file_name).write_bytes(content)

#         image = image_model.Image(
#             post_id=db_post.id,
#             orig_name=file.filename,
#             media_type=(file.content_type or "application/octet-stream"),
#             file_size=len(content),
#             path=f"/uploads/images/{file_name}",
#         )
#         image_repo.create_image(db, image)


async def verify_post_owner(db: Session, post_id: UUID, clerk_id: str) -> model.Post:
    user = await get_user_by_clerk_id(db, clerk_id)
    post = repo.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not user or post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    return post

async def list_posts(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    state: str | None = "published",
    status: str | None = "active",
    clerk_id: str | None = None
):
    user_id = None
    if clerk_id:
        user = await get_user_by_clerk_id(db, clerk_id)
        if user:
            user_id = user.id

    return repo.list_posts(db, category, q, sort, state, status, user_id=user_id)

def get_post(db: Session, post_id: UUID):
    post = repo.get_post(db, post_id)
    if not post:
        raise ValueError("Post not found")
    return post

def get_posts_by_user_id(db: Session, user_id: UUID):
    return repo.list_posts(db, user_id=user_id)

def update_post(db: Session, post_id: UUID, post_data: schema.PostUpdate):
    db_post = get_post(db, post_id)
    return repo.update_post(db, db_post, post_data)

# Service to change post status
def change_post_status(db: Session, post_id: UUID, status: schema.PostStatus):
    db_post = get_post(db, post_id)
    # Add business logic for allowed transitions if needed
    return repo.update_post_status(db, db_post, status)

def delete_post(db: Session, post_id: UUID):
    db_post = get_post(db, post_id)

    for media in list(db_post.media):
        if media.path:
            ap = _abs(media.path)
            if os.path.exists(ap):
                os.remove(ap)
        media_repo.delete_media(db, media)

    for camp in list(db_post.campaigns):
        for media in list(camp.media):
            if media.path:
                ap = _abs(media.path)
                if os.path.exists(ap):
                    os.remove(ap)
            media_repo.delete_media(db, media)
    
    for reward in list(db_post.rewards):
        for media in list(reward.media):
            if media.path:
                ap = _abs(media.path)
                if os.path.exists(ap):
                    os.remove(ap)
            media_repo.delete_media(db, media)

    return repo.delete_post(db, db_post)


async def create_post(
    db: Session,
    *,
    clerk_id: str,
    post_data: schema.PostCreate,
    post_media: Optional[List[UploadFile]] = None,
    post_media_manifest: Optional[list[dict]] = None,
    campaigns: Optional[List[dict]] = None, 
    campaign_media: Optional[List[UploadFile]] = None,
    rewards: Optional[List[dict]] = None,
    reward_media: Optional[List[UploadFile]] = None,
):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1) create post
    db_post = repo.create_post_by_user(db, user_id=user.id, data=post_data)

    predict_input = {
        "goal": post_data.goal_amount,
        "name": post_data.post_header,
        "blurb": post_data.post_description or "",
        "start_date": format_datetime(post_data.effective_start_from),
        "end_date": format_datetime(post_data.effective_end_date),
        "country_displayable_name": country_service.get_country(db, user.country_id).en_name,
        "category_group": post_data.category.value if post_data.category else "other",
        "has_video": 0,
        "has_photo": 1 if post_media else 0,
    }

    input_model = model_schema.InputData(**predict_input)

    await model_service.predict(db,input_model,db_post.id,True)

    # 2) post media
    await media_service._save_files_and_create_media(
        db, parent_type="post", parent_id=db_post.id,
        files=post_media or [], media_manifest=post_media_manifest or []
    )

    # 3) campaigns
    if campaigns:
        files = campaign_media or []

        for idx, item in enumerate(campaigns):
            payload = {k: v for k, v in item.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)
            create_obj = campaign_schema.CampaignCreate(**payload)

            await campaign_service.create_campaign_with_media(
                db=db, campaign_data=[create_obj], files=[files[idx]]
            )

    if rewards:
        rfiles = reward_media or []
        for idx, item in enumerate(rewards):
            payload = {k: v for k, v in item.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)
            rcreate = reward_schema.RewardCreate(**payload)

            await reward_service.create_reward_with_media(
                db=db, reward_data=[rcreate], files=[rfiles[idx]]
            )

    return repo.get_post(db, db_post.id)


async def update_post(
    db: Session,
    *,
    post_id: UUID,
    clerk_id: str,
    post_data: Optional[schema.PostUpdate] = None,
    post_media: Optional[List[UploadFile]] = None,       
    campaigns_payload: Optional[List[dict]] = None,       
    campaign_media: Optional[List[UploadFile]] = None,
    rewards_payload: Optional[List[dict]] = None,
    reward_media: Optional[List[UploadFile]] = None,
    post_media_manifest: Optional[list[dict]] = None,
    post_media_reorder: Optional[list[dict]] = None,
):
    db_post = await verify_post_owner(db, post_id, clerk_id)

    # 1) update post fields
    if post_data:
        repo.update_post(db, db_post, post_data)

    # 2) Manage Images
    # A. Handle Existing Images (Reorder + Delete)
    if post_media_reorder is not None:
        # 1. Parse payload
        id_to_order = {UUID(str(it["id"])): int(it["display_order"]) for it in post_media_reorder}
        
        # 2. Identify current media in DB
        current_media = {img.id: img for img in db_post.media}
        
        # 3. Update Order for kept media
        for media_id, order in id_to_order.items():
            if media_id in current_media:
                current_media[media_id].display_order = order
        
        # 4. Delete missing media (Existing in DB but NOT in reorder list) 
        kept_ids = set(id_to_order.keys())
        for media_id, media in current_media.items():
            if media_id not in kept_ids:
                # Delete physical file
                if media.path:
                    ap = _abs(media.path)
                    try:
                        if os.path.exists(ap):
                            os.remove(ap)
                    except Exception as e:
                        print(f"Error deleting file {ap}: {e}")
                # Delete from DB
                media_repo.delete_media(db, media)
        
        db.commit()

    # B. Add New Media
    if post_media:
        await media_service._save_files_and_create_media(
            db,
            parent_type="post",
            parent_id=db_post.id,
            files=post_media, # already a list or None
            media_manifest=post_media_manifest or [],   
        )

    # --- campaigns ---
    if campaigns_payload is not None:
        imgs = campaign_media or []
        ptr = 0

        current = {str(c.id): c for c in db_post.campaigns}
        existing_ids = set(current.keys())

        incoming_ids = set(str(it["id"]) for it in campaigns_payload if it.get("id"))
        to_delete_ids   = existing_ids - incoming_ids
        to_update_items = [it for it in campaigns_payload if it.get("id") and str(it["id"]) in existing_ids]
        to_create_items = [it for it in campaigns_payload if not it.get("id") or str(it["id"]) not in existing_ids]

        # delete
        for cid in to_delete_ids:
            await campaign_service.delete_campaign(db=db, campaign_id=UUID(cid))

        # update 
        for it in to_update_items:
            cid = UUID(it["id"])
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            upd_obj = campaign_schema.CampaignUpdate(**payload)

            file = None
            if it.get("isEdited"):            
                if ptr >= len(imgs):
                    raise HTTPException(status_code=400, detail="Missing campaign image for edited item")
                file = imgs[ptr]; ptr += 1

            await campaign_service.update_campaign_with_media(
                db=db, campaign_id=cid, campaign_data=upd_obj, files=([file] if file else None)
            )

        # create
        for it in to_create_items:
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)

            if ptr >= len(imgs):
                raise HTTPException(status_code=400, detail="New campaign requires an image")
            file = imgs[ptr]; ptr += 1

            await campaign_service.create_campaign_with_media(
                db=db, campaign_data=[campaign_schema.CampaignCreate(**payload)], files=[file]
            )

        
    # --- rewards ---
    if rewards_payload is not None:
        imgs = reward_media or []
        ptr = 0

        current = {str(c.id): c for c in db_post.rewards}
        existing_ids = set(current.keys())

        incoming_ids = set(str(it["id"]) for it in rewards_payload if it.get("id"))
        to_delete_ids   = existing_ids - incoming_ids
        to_update_items = [it for it in rewards_payload if it.get("id") and str(it["id"]) in existing_ids]
        to_create_items = [it for it in rewards_payload if not it.get("id") or str(it["id"]) not in existing_ids]

        # delete
        for rid in to_delete_ids:
            await reward_service.delete_reward(db=db, reward_id=UUID(rid))

        # update 
        for it in to_update_items:
            rid = UUID(it["id"])
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            upd_obj = reward_schema.RewardUpdate(**payload)

            file = None
            if it.get("isEdited"):             
                if ptr >= len(imgs):
                    raise HTTPException(status_code=400, detail="Missing reward image for edited item")
                file = imgs[ptr]; ptr += 1

            await reward_service.update_reward_with_media(
                db=db, reward_id=rid, reward_data=upd_obj, files=([file] if file else None)
            )

        # create 
        for it in to_create_items:
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)

            if ptr >= len(imgs):
                raise HTTPException(status_code=400, detail="New reward requires an image")
            file = imgs[ptr]; ptr += 1

            await reward_service.create_reward_with_media(
                db=db, reward_data=[reward_schema.RewardCreate(**payload)], files=[file]
            )

    return repo.get_post(db, post_id)


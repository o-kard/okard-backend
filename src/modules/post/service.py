import os
from typing import List, Optional
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy import Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.image import model as image_model, repo as image_repo, service as image_service
from src.modules.campaign import schema as campaign_schema, service as campaign_service
from src.modules.reward import schema as reward_schema, service as reward_service
from pathlib import Path
from src.modules.user.repo import get_user_by_clerk_id 
import os
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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


def verify_post_owner(db: Session, post_id: UUID, clerk_id: str) -> model.Post:
    user = get_user_by_clerk_id(db, clerk_id)
    post = repo.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not user or post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    return post

def list_posts(db: Session):
    return repo.list_posts(db)

def get_post(db: Session, post_id: UUID):
    post = repo.get_post(db, post_id)
    if not post:
        raise ValueError("Post not found")
    return post

def update_post(db: Session, post_id: UUID, post_data: schema.PostUpdate):
    db_post = get_post(db, post_id)
    return repo.update_post(db, db_post, post_data)

def delete_post(db: Session, post_id: UUID):
    db_post = get_post(db, post_id)

    for image in list(db_post.images):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)

    for camp in list(db_post.campaigns):
        for image in list(camp.image):
            if image.path:
                ap = _abs(image.path)
                if os.path.exists(ap):
                    os.remove(ap)
    
    for reward in list(db_post.rewards):
        for image in list(reward.image):
            if image.path:
                ap = _abs(image.path)
                if os.path.exists(ap):
                    os.remove(ap)

    return repo.delete_post(db, db_post)


async def create_post(
    db: Session,
    *,
    clerk_id: str,
    post_data: schema.PostCreate,
    post_images: Optional[List[UploadFile]] = None,
    post_images_manifest = None,
    campaigns: Optional[List[dict]] = None, 
    campaign_images: Optional[List[UploadFile]] = None,
    rewards: Optional[List[dict]] = None,
    reward_images: Optional[List[UploadFile]] = None,
):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1) create post
    db_post = repo.create_post_by_user(db, user_id=user.id, data=post_data)

    # 2) post images
    await image_service._save_files_and_create_images(
        db, parent_type="post", parent_id=db_post.id,
        files=post_images or [], images_manifest=post_images_manifest or []
    )

    # 3) campaigns
    if campaigns:
        files = campaign_images or []

        for idx, item in enumerate(campaigns):
            payload = {k: v for k, v in item.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)
            create_obj = campaign_schema.CampaignCreate(**payload)

            await campaign_service.create_campaign_with_images(
                db=db, campaign_data=[create_obj], files=[files[idx]]
            )

    if rewards:
        rfiles = reward_images or []
        for idx, item in enumerate(rewards):
            payload = {k: v for k, v in item.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)
            rcreate = reward_schema.RewardCreate(**payload)

            await reward_service.create_reward_with_images(
                db=db, reward_data=[rcreate], files=[rfiles[idx]]
            )

    return repo.get_post(db, db_post.id)


async def update_post(
    db: Session,
    *,
    post_id: UUID,
    clerk_id: str,
    post_data: Optional[schema.PostUpdate] = None,
    post_images: Optional[List[UploadFile]] = None,       
    campaigns_payload: Optional[List[dict]] = None,       
    campaign_images: Optional[List[UploadFile]] = None,
    rewards_payload: Optional[List[dict]] = None,
    reward_images: Optional[List[UploadFile]] = None,
    post_images_manifest: Optional[list[dict]] = None,
    post_images_reorder: Optional[list[dict]] = None, 
):
    db_post = verify_post_owner(db, post_id, clerk_id)

    # 1) update post fields
    if post_data:
        repo.update_post(db, db_post, post_data)

    # 2) post images: BULK REPLACE
    if post_images is not None:
        for image in list(db_post.images):
            if image.path:
                ap = _abs(image.path)
                if os.path.exists(ap):
                    os.remove(ap)
            db.delete(image)
        db.commit()

        await image_service._save_files_and_create_images(
            db,
            parent_type="post",
            parent_id=db_post.id,
            files=post_images or [],
            images_manifest=post_images_manifest or [],   
        )

    elif post_images_reorder:
        id_to_order = {UUID(str(it["id"])): int(it["order"]) for it in post_images_reorder}
        current = {img.id: img for img in db_post.images}
        unknown = [str(i) for i in id_to_order.keys() if i not in current]
        if unknown:
            raise HTTPException(status_code=400, detail=f"Unknown image ids: {unknown}")

        for img_id, ord_ in id_to_order.items():
            current[img_id].order = ord_
        db.commit()

    # --- campaigns ---
    if campaigns_payload is not None:
        imgs = campaign_images or []
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

            await campaign_service.update_campaign_with_images(
                db=db, campaign_id=cid, campaign_data=upd_obj, files=([file] if file else None)
            )

        # create
        for it in to_create_items:
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)

            if ptr >= len(imgs):
                raise HTTPException(status_code=400, detail="New campaign requires an image")
            file = imgs[ptr]; ptr += 1

            await campaign_service.create_campaign_with_images(
                db=db, campaign_data=[campaign_schema.CampaignCreate(**payload)], files=[file]
            )

        
    # --- rewards ---
    if rewards_payload is not None:
        imgs = reward_images or []
        ptr = 0

        current = {str(c.id): c for c in db_post.rewards}
        existing_ids = set(current.keys())

        incoming_ids = set(str(it["id"]) for it in rewards_payload if it.get("id"))
        to_delete_ids   = existing_ids - incoming_ids
        to_update_items = [it for it in rewards_payload if it.get("id") and str(it["id"]) in existing_ids]
        to_create_items = [it for it in rewards_payload if not it.get("id") or str(it["id"]) not in existing_ids]

        # delete
        for cid in to_delete_ids:
            await reward_service.delete_reward(db=db, reward_id=UUID(cid))

        # update 
        for it in to_update_items:
            cid = UUID(it["id"])
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            upd_obj = reward_schema.RewardUpdate(**payload)

            file = None
            if it.get("isEdited"):             
                if ptr >= len(imgs):
                    raise HTTPException(status_code=400, detail="Missing reward image for edited item")
                file = imgs[ptr]; ptr += 1

            await reward_service.update_reward_with_images(
                db=db, reward_id=cid, reward_data=upd_obj, files=([file] if file else None)
            )

        # create 
        for it in to_create_items:
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            payload.setdefault("post_id", db_post.id)

            if ptr >= len(imgs):
                raise HTTPException(status_code=400, detail="New reward requires an image")
            file = imgs[ptr]; ptr += 1

            await reward_service.create_reward_with_images(
                db=db, reward_data=[reward_schema.RewardCreate(**payload)], files=[file]
            )

    return repo.get_post(db, post_id)


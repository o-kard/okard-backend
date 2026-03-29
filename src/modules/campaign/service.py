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
from src.modules.information import schema as info_schema, service as info_service
from src.modules.reward import schema as reward_schema, service as reward_service
from src.modules.model import service as model_service, schema as model_schema, repo as model_repo
from src.modules.country import service as country_service
from pathlib import Path
from src.modules.user.service import get_user_by_clerk_id
from src.modules.common.enums import CampaignState
from src.modules.user.repo import get_user_by_id
from src.modules.common.enums import UserRole
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


async def verify_campaign_owner(db: Session, campaign_id: UUID, clerk_id: str) -> model.Campaign:
    user = await get_user_by_clerk_id(db, clerk_id)
    campaign = repo.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Allow if user is owner OR if user is admin
    if not user or (campaign.user_id != user.id and user.role != UserRole.admin):
        raise HTTPException(status_code=403, detail="Permission denied")
    return campaign

async def list_campaigns(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    state: str | None = "published",
    clerk_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    include_closed: bool = True
):
    user_id = None
    if clerk_id:
        user = await get_user_by_clerk_id(db, clerk_id)
        if user:
            user_id = user.id

    return repo.list_campaigns(db, category, q, sort, state, current_user_id=user_id, limit=limit, offset=offset, include_closed=include_closed)

async def list_campaign_pagination(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    state: str | None = "published",
    clerk_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    include_closed: bool = True
):
    user_id = None
    if clerk_id:
        user = await get_user_by_clerk_id(db, clerk_id)
        if user:
            user_id = user.id
    return repo.list_campaigns_paginated(db, category, q, sort, state, user_id, None, limit, offset, include_closed)

def get_campaign(db: Session, campaign_id: UUID, user_id: UUID | None = None):
    campaign = repo.get_campaign(db, campaign_id, user_id)
    if not campaign:
        raise ValueError("Campaign not found")
        
    if campaign.state == CampaignState.draft:
        if not user_id or campaign.user_id != user_id:
            raise ValueError("Permission denied. Cannot view draft campaign.")
            
    return campaign

def get_campaigns_by_user_id(db: Session, user_id: UUID):
    return repo.list_campaigns(db, owner_id=user_id, state="all")

def update_campaign(db: Session, campaign_id: UUID, campaign_data: schema.CampaignUpdate):
    db_campaign = get_campaign(db, campaign_id)
    return repo.update_campaign(db, db_campaign, campaign_data)

# Service to change campaign state
def change_campaign_state(db: Session, campaign_id: UUID, state: schema.CampaignState):
    db_campaign = get_campaign(db, campaign_id)
    # Add business logic for allowed transitions if needed
    return repo.update_campaign_state(db, db_campaign, state)

def delete_campaign(db: Session, campaign_id: UUID):
    db_campaign = get_campaign(db, campaign_id)

    for media in list(db_campaign.media):
        if media.path:
            ap = _abs(media.path)
            if os.path.exists(ap):
                os.remove(ap)
        media_repo.delete_media(db, media)

    for info in list(db_campaign.informations):
        for media in list(info.media):
            if media.path:
                ap = _abs(media.path)
                if os.path.exists(ap):
                    os.remove(ap)
            media_repo.delete_media(db, media)
    
    for reward in list(db_campaign.rewards):
        for media in list(reward.media):
            if media.path:
                ap = _abs(media.path)
                if os.path.exists(ap):
                    os.remove(ap)
            media_repo.delete_media(db, media)

    return repo.delete_campaign(db, db_campaign)


async def create_campaign(
    db: Session,
    *,
    clerk_id: str,
    campaign_data: schema.CampaignCreate,
    campaign_media: Optional[List[UploadFile]] = None,
    campaign_media_manifest: Optional[list[dict]] = None,
    informations: Optional[List[dict]] = None, 
    information_media: Optional[List[UploadFile]] = None,
    rewards: Optional[List[dict]] = None,
    reward_media: Optional[List[UploadFile]] = None,
):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1) create campaign
    db_campaign = repo.create_campaign_by_user(db, user_id=user.id, data=campaign_data)

    predict_input = {
        "goal": campaign_data.goal_amount,
        "name": campaign_data.campaign_header,
        "blurb": campaign_data.campaign_description or "",
        "start_date": format_datetime(campaign_data.effective_start_from),
        "end_date": format_datetime(campaign_data.effective_end_date),
        "country_displayable_name": country_service.get_country(db, user.country_id).en_name,
        "category_group": campaign_data.category.value if campaign_data.category else "other",
        "has_video": any(m.get("type") == "video" for m in (campaign_media_manifest or [])),
        "has_photo": any(m.get("type") == "image" for m in (campaign_media_manifest or [])),
    }

    input_model = model_schema.InputData(**predict_input)

    await model_service.predict(db,input_model,db_campaign.id,True)

    # 2) campaign media
    await media_service._save_files_and_create_media(
        db, parent_type="campaign", parent_id=db_campaign.id,
        files=campaign_media or [], media_manifest=campaign_media_manifest or []
    )

    # 3) informations
    if informations:
        files = information_media or []

        for idx, item in enumerate(informations):
            payload = {k: v for k, v in item.items() if k not in ["id", "isEdited"]}
            payload.setdefault("campaign_id", db_campaign.id)
            create_obj = info_schema.InformationCreate(**payload)

            await info_service.create_information_with_media(
                db=db, information_data=[create_obj], files=[files[idx]]
            )

    if rewards:
        rfiles = reward_media or []
        for idx, item in enumerate(rewards):
            payload = {k: v for k, v in item.items() if k not in ["id", "isEdited"]}
            payload.setdefault("campaign_id", db_campaign.id)
            rcreate = reward_schema.RewardCreate(**payload)

            await reward_service.create_reward_with_media(
                db=db, reward_data=[rcreate], files=[rfiles[idx]]
            )

    return repo.get_campaign(db, db_campaign.id)


async def update_campaign(
    db: Session,
    *,
    campaign_id: UUID,
    clerk_id: str,
    campaign_data: Optional[schema.CampaignUpdate] = None,
    campaign_media: Optional[List[UploadFile]] = None,       
    informations_payload: Optional[List[dict]] = None,       
    information_media: Optional[List[UploadFile]] = None,
    rewards_payload: Optional[List[dict]] = None,
    reward_media: Optional[List[UploadFile]] = None,
    campaign_media_manifest: Optional[list[dict]] = None,
    campaign_media_reorder: Optional[list[dict]] = None,
):
    db_campaign = await verify_campaign_owner(db, campaign_id, clerk_id)

    # 1) update campaign fields
    if campaign_data:
        # If there are supporters, prevent direct update of critical fields (must use Edit Request)
        if db_campaign.supporter > 0:
            if campaign_data.goal_amount is not None and campaign_data.goal_amount != db_campaign.goal_amount:
                raise HTTPException(
                    status_code=400, 
                    detail="Goal amount cannot be updated directly once there are supporters. Please submit an Edit Request."
                )
            
            if campaign_data.effective_end_date is not None and campaign_data.effective_end_date != db_campaign.effective_end_date:
                raise HTTPException(
                    status_code=400, 
                    detail="Campaign end date cannot be updated directly once there are supporters. Please submit an Edit Request."
                )

        repo.update_campaign(db, db_campaign, campaign_data)

    # 2) Manage Images
    # A. Handle Existing Images (Reorder + Delete)
    if campaign_media_reorder is not None:
        # 1. Parse payload
        id_to_order = {UUID(str(it["id"])): int(it["display_order"]) for it in campaign_media_reorder}
        
        # 2. Identify current media in DB
        current_media = {img.id: img for img in db_campaign.media}
        
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
    if campaign_media:
        await media_service._save_files_and_create_media(
            db,
            parent_type="campaign",
            parent_id=db_campaign.id,
            files=campaign_media, # already a list or None
            media_manifest=campaign_media_manifest or [],   
        )

    # --- informations ---
    if informations_payload is not None:
        imgs = information_media or []
        ptr = 0

        current = {str(c.id): c for c in db_campaign.informations}
        existing_ids = set(current.keys())

        incoming_ids = set(str(it["id"]) for it in informations_payload if it.get("id"))
        to_delete_ids   = existing_ids - incoming_ids
        to_update_items = [it for it in informations_payload if it.get("id") and str(it["id"]) in existing_ids]
        to_create_items = [it for it in informations_payload if not it.get("id") or str(it["id"]) not in existing_ids]

        # delete
        for cid in to_delete_ids:
            await info_service.delete_information(db=db, information_id=UUID(cid))

        # update 
        for it in to_update_items:
            cid = UUID(it["id"])
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            upd_obj = info_schema.InformationUpdate(**payload)

            file = None
            if it.get("isEdited"):            
                if ptr >= len(imgs):
                    raise HTTPException(status_code=400, detail="Missing information image for edited item")
                file = imgs[ptr]; ptr += 1

            await info_service.update_information_with_media(
                db=db, information_id=cid, information_data=upd_obj, files=([file] if file else None)
            )

        # create
        for it in to_create_items:
            payload = {k: v for k, v in it.items() if k not in ["id", "isEdited"]}
            payload.setdefault("campaign_id", db_campaign.id)

            if ptr >= len(imgs):
                raise HTTPException(status_code=400, detail="New information requires an image")
            file = imgs[ptr]; ptr += 1

            await info_service.create_information_with_media(
                db=db, information_data=[info_schema.InformationCreate(**payload)], files=[file]
            )

        
    # --- rewards ---
    if rewards_payload is not None:
        imgs = reward_media or []
        ptr = 0

        current = {str(c.id): c for c in db_campaign.rewards}
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
            payload.setdefault("campaign_id", db_campaign.id)

            if ptr >= len(imgs):
                raise HTTPException(status_code=400, detail="New reward requires an image")
            file = imgs[ptr]; ptr += 1

            await reward_service.create_reward_with_media(
                db=db, reward_data=[reward_schema.RewardCreate(**payload)], files=[file]
            )

    await update_prediction_for_campaign(db, campaign_id)

    return repo.get_campaign(db, campaign_id)


async def update_prediction_for_campaign(db: Session, campaign_id: UUID):
    db_campaign = repo.get_campaign(db, campaign_id)
    if not db_campaign:
        return
    
    user = get_user_by_id(db, db_campaign.user_id)
    if not user:
        return
    
    has_video = any((m.media_type or "").startswith("video/") for m in db_campaign.media)
    has_photo = any(not (m.media_type or "").startswith("video/") for m in db_campaign.media)

    predict_input = {
        "goal": db_campaign.goal_amount,
        "name": db_campaign.campaign_header,
        "blurb": db_campaign.campaign_description or "",
        "start_date": format_datetime(db_campaign.effective_start_from),
        "end_date": format_datetime(db_campaign.effective_end_date),
        "country_displayable_name": country_service.get_country(db, user.country_id).en_name,
        "category_group": db_campaign.category.value if db_campaign.category else "other",
        "has_video": has_video,
        "has_photo": has_photo,
    }

    input_model = model_schema.InputData(**predict_input)
    await model_service.predict(db, input_model, db_campaign.id, save=True)

async def get_campaign_community_stats(db: Session, campaign_id: UUID):
    db_campaign = repo.get_campaign(db, campaign_id)
    if not db_campaign:
        raise ValueError("Campaign not found")
    return repo.get_campaign_community_stats(db, campaign_id)


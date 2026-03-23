from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional, Union
import json
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from src.modules.information import schema as info_schema, service as info_service
from fastapi import Form 
from . import repo
from src.modules.model import controller as predict_controller
from src.modules.model.schema import InputData
from src.modules.auth import get_current_user, get_optional_current_user

from fastapi import BackgroundTasks
from src.modules.campaign.background import generate_campaign_embedding
from src.modules.campaign_view.service import log_campaign_view
from src.modules.user.repo import get_user_by_clerk_id

from src.modules.campaign_recommend import service as recommend_service
from src.modules.campaign_recommend import schema as recommend_schema

from src.modules.for_you import service as for_you_service
from src.modules.for_you import schema as for_you_schema
from src.modules.common.file_utils import validate_image_size
from src.modules.user.service import check_user_active

router = APIRouter(prefix="/campaign", tags=["Campaign"])

@router.get("", response_model=list[schema.CampaignOut])
async def list_campaigns(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query("newest"),
    state: Optional[str] = Query("published"),
    clerk_id: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    include_closed: bool = Query(True),
    db: Session = Depends(get_db)
):
    return await service.list_campaigns(db, category, q, sort, state, clerk_id, limit, offset, include_closed)

@router.get("/campaign-by-user/{user_id}", response_model=List[schema.CampaignOut])
def fetch_campaigns_by_user_id(user_id: UUID, db: Session = Depends(get_db)):
    return service.get_campaigns_by_user_id(db, user_id)
    
@router.get("/{campaign_id}", response_model=schema.CampaignOut)
async def get_campaign(
    campaign_id: UUID,
    payload: Optional[dict] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = None
    if payload:
        clerk_id = payload.get("sub")
        try:
            user = get_user_by_clerk_id(db, clerk_id)
            if user:
                user_id = user.id
                log_campaign_view(db, user.id, campaign_id)
        except Exception as e:
            print(f"Error logging view or fetching user: {e}")

    try:
        campaign = service.get_campaign(db, campaign_id, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

    return campaign

@router.delete("/{campaign_id}", response_model=schema.CampaignOut)
def delete(campaign_id: UUID,clerk_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        service.verify_campaign_owner(db, campaign_id, clerk_id)
        return service.delete_campaign(db, campaign_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/with-informations", response_model=schema.CampaignOut)
async def create(
    campaign_data: str = Form(...),
    media: Union[List[UploadFile], UploadFile, None] = File(None),
    media_manifest: Union[str, None] = Form(None),
    informations: Union[str, None] = Form(None),                                  
    information_media: Union[List[UploadFile], UploadFile, None] = File(None),
    rewards: Union[str, None] = Form(None),                     
    reward_media: Union[List[UploadFile], UploadFile, None] = File(None),     
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    await check_user_active(db, clerk_id)
    
    try:
        campaign_obj = schema.CampaignCreate(**json.loads(campaign_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid campaign_data")

    campaign_media_list: Optional[List[UploadFile]] = None
    if media is not None:
        campaign_media_list = media if isinstance(media, list) else [media]
        for f in campaign_media_list:
            validate_image_size(f)

    info_list_raw = None
    if informations:
        parsed = json.loads(informations)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid informations payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid informations payload")
        info_list_raw = parsed

    info_media_list: Optional[List[UploadFile]] = None
    if information_media is not None:
        info_media_list = information_media if isinstance(information_media, list) else [information_media]
        for f in info_media_list:
            validate_image_size(f)

    reward_list_raw = None
    if rewards:
        parsed = json.loads(rewards)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid rewards payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid rewards payload")
        reward_list_raw = parsed

    reward_media_list = None
    if reward_media is not None:
        reward_media_list = reward_media if isinstance(reward_media, list) else [reward_media]
        for f in reward_media_list:
            validate_image_size(f)

    if not info_list_raw or len(info_list_raw) == 0:
        raise HTTPException(status_code=400, detail="At least one information entry is required.")
    if not info_media_list or len(info_media_list) != len(info_list_raw):
        raise HTTPException(status_code=400, detail="information_media must match informations count (1:1).")

    if not reward_list_raw or len(reward_list_raw) == 0:
        raise HTTPException(status_code=400, detail="At least one reward entry is required.")
    if not reward_media_list or len(reward_media_list) != len(reward_list_raw):
        raise HTTPException(status_code=400, detail="reward_media must match rewards count (1:1).")
        
    campaign_media_list = media if isinstance(media, list) else ([media] if media else [])
    manifest = json.loads(media_manifest) if media_manifest else []
        
    campaign = await service.create_campaign(
        db=db, clerk_id=clerk_id, campaign_data=campaign_obj,
        campaign_media=campaign_media_list,
        campaign_media_manifest=manifest,
        informations=info_list_raw, information_media=info_media_list,
        rewards=reward_list_raw, reward_media=reward_media_list,
    )
    
    if background_tasks:
        print("Background tasks enabled")
        print('campaign id: ', campaign.id)
        print('generate campaign embedding')
        background_tasks.add_task(generate_campaign_embedding, campaign.id)
        print('generate campaign embedding done')

    return campaign
    

@router.put("/{campaign_id}/with-informations", response_model=schema.CampaignOut)
async def update(
    campaign_id: UUID,
    campaign_data: Union[str, None] = Form(None),
    media: Union[List[UploadFile], UploadFile, None] = File(None),              
    informations: Union[str, None] = Form(None),                                 
    information_media: Union[List[UploadFile], UploadFile, None] = File(None),
    rewards: Union[str, None] = Form(None),                                 
    reward_media: Union[List[UploadFile], UploadFile, None] = File(None),          
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
    media_manifest: Union[str, None] = Form(None),         
    media_reorder: Union[str, None] = Form(None),   
    background_tasks: BackgroundTasks = None,
):
    await check_user_active(db, clerk_id)

    # --- parse campaign_data ---
    campaign_upd = None
    if campaign_data:
        try:
            campaign_upd = schema.CampaignUpdate(**json.loads(campaign_data))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid campaign_data")

    # --- normalize media fields ---
    campaign_media_list: Optional[List[UploadFile]] = None
    if media is not None:
        campaign_media_list = media if isinstance(media, list) else [media]
        for f in campaign_media_list:
            validate_image_size(f)

    info_media_list: Optional[List[UploadFile]] = None
    if information_media is not None:
        info_media_list = information_media if isinstance(information_media, list) else [information_media]
        for f in info_media_list:
            validate_image_size(f)

    reward_media_list: Optional[List[UploadFile]] = None
    if reward_media is not None:
        reward_media_list = reward_media if isinstance(reward_media, list) else [reward_media]
        for f in reward_media_list:
            validate_image_size(f)

    # --- parse informations manifest (list[dict]) ---
    info_payload = None
    if informations:
        parsed = json.loads(informations)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid informations payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid informations payload")
        info_payload = parsed

    reward_payload = None
    if rewards:
        parsed = json.loads(rewards)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid rewards payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid rewards payload")
        reward_payload = parsed

    campaign_media_list = media if isinstance(media, list) else ([media] if media else None)
    media_manifest_parsed = json.loads(media_manifest) if media_manifest else None
    reorder_list = json.loads(media_reorder) if media_reorder else None

    # --- call service ---
    campaign = await service.update_campaign(
        db=db,
        campaign_id=campaign_id,
        clerk_id=clerk_id,
        campaign_data=campaign_upd,
        campaign_media=campaign_media_list,    
        informations_payload=info_payload,  
        information_media=info_media_list,
        rewards_payload=reward_payload,  
        reward_media=reward_media_list,
        campaign_media_manifest=media_manifest_parsed,           
        campaign_media_reorder=reorder_list, 
    )
    if background_tasks and campaign_data:
        print("Background tasks enabled")
        print('campaign id: ', campaign.id)
        print('generate campaign embedding')
        background_tasks.add_task(generate_campaign_embedding, campaign.id)
        print('generate campaign embedding done')

    return campaign
    
@router.put("/{campaign_id}/state", response_model=schema.CampaignOut)
async def update_campaign_state(
    campaign_id: UUID,
    state: schema.CampaignState = Query(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
): 
    clerk_id = current_user["sub"]
    await check_user_active(db, clerk_id)

    try:
        service.verify_campaign_owner(db, campaign_id, clerk_id)
        return service.change_campaign_state(db, campaign_id, state)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.get("/{campaign_id}/community", response_model=schema.CampaignCommunityOut)
async def get_campaign_community(campaign_id: UUID, db: Session = Depends(get_db)):
    try:
        return await service.get_campaign_community_stats(db, campaign_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Campaign not found")
  
# @router.post("/predict/{post_id}")
# async def predict_post(post_id: UUID, db: Session = Depends(get_db)):
#     post = repo.get_post_by_id(db, post_id)
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     # ✅ เตรียมข้อมูลจาก DB ให้ตรงกับ InputData ของ model
#     data = {
#         "goal": post.goal_amount,
#         "name": post.post_header,
#         "blurb": post.post_description,
#         "start_date": post.effective_start_from.isoformat() if post.effective_start_from else None,
#         "end_date": post.effective_end_date.isoformat() if post.effective_end_date else None,
#         "country_displayable_name": post.country_name,
#         "has_video": 0,
#         "has_photo": 1,
#     }

#     # ✅ เรียก predict() ที่คุณมีอยู่อีกไฟล์โดยตรง
#     result = await predict_controller.predict(InputData(**data))

#     # ✅ อัปเดตผลลัพธ์กลับ DB
#     repo.update_post_prediction(db, post_id, result)
#     db.commit()

#     return {"message": "Prediction completed", "result": result}


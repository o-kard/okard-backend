from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional, Union
import json
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from src.modules.campaign import schema as camp_schema, service as camp_service
from fastapi import Form 
from src.modules.post import repo
from src.modules.model import controller as predict_controller
from src.modules.model.schema import InputData
from src.modules.auth import get_current_user

from fastapi import BackgroundTasks
from src.modules.post.background import generate_post_embedding
from src.modules.post_view.service import log_post_view
from src.modules.user.repo import get_user_by_clerk_id

from src.modules.post_recommend import service as recommend_service
from src.modules.post_recommend import schema as recommend_schema

from src.modules.for_you import service as for_you_service
from src.modules.for_you import schema as for_you_schema

router = APIRouter(prefix="/post", tags=["Post"])

@router.get("", response_model=list[schema.PostOut])
async def list_posts(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query("newest"),
    state: Optional[str] = Query("published"),
    status: Optional[str] = Query("active"),
    clerk_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return await service.list_posts(db, category, q, sort, state, status, clerk_id)

@router.get("/campaign-by-user/{user_id}", response_model=List[schema.PostOut])
def fetch_posts_by_user_id(user_id: UUID, db: Session = Depends(get_db)):
    return service.get_posts_by_user_id(db, user_id)
    
@router.get("/{post_id}", response_model=schema.PostOut)
def get_post(post_id: UUID, clerk_id: str | None = Query(None), db: Session = Depends(get_db)):
    try:
        post = service.get_post(db, post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

    if clerk_id:
        try:
            user = get_user_by_clerk_id(db, clerk_id)
            if user:
                log_post_view(db, user.id, post_id)
        except Exception as e:
            print(f"Error logging view: {e}")

    return post

@router.delete("/{post_id}", response_model=schema.PostOut)
def delete(post_id: UUID,clerk_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        service.verify_post_owner(db, post_id, clerk_id)
        return service.delete_post(db, post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/with-campaigns", response_model=schema.PostOut)
async def create(
    post_data: str = Form(...),
    media: Union[List[UploadFile], UploadFile, None] = File(None),
    media_manifest: Union[str, None] = Form(None),
    campaigns: Union[str, None] = Form(None),                                  
    campaign_media: Union[List[UploadFile], UploadFile, None] = File(None),
    rewards: Union[str, None] = Form(None),                     
    reward_media: Union[List[UploadFile], UploadFile, None] = File(None),     
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    # print("post_media:", len(media or []))
    # print("create_campaigns:", len(campaigns or []), "camp_files:", len(campaign_media or []))
    
    try:
        post_obj = schema.PostCreate(**json.loads(post_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid post_data")

    post_media_list: Optional[List[UploadFile]] = None
    if media is not None:
        post_media_list = media if isinstance(media, list) else [media]

    camp_list_raw = None
    if campaigns:
        parsed = json.loads(campaigns)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid campaigns payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid campaigns payload")
        camp_list_raw = parsed

    camp_media_list: Optional[List[UploadFile]] = None
    if campaign_media is not None:
        camp_media_list = campaign_media if isinstance(campaign_media, list) else [campaign_media]

    if camp_list_raw is not None:
        if not camp_media_list or len(camp_media_list) != len(camp_list_raw):
            raise HTTPException(status_code=400, detail="campaign_media must match campaigns count (1:1).")

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

    if reward_list_raw is not None:
        if not reward_media_list or len(reward_media_list) != len(reward_list_raw):
            raise HTTPException(status_code=400, detail="reward_media must match rewards count (1:1).")
        
    post_media_list = media if isinstance(media, list) else ([media] if media else [])
    manifest = json.loads(media_manifest) if media_manifest else []
        
    post = await service.create_post(
        db=db, clerk_id=clerk_id, post_data=post_obj,
        post_media=post_media_list,
        post_media_manifest=manifest,
        campaigns=camp_list_raw, campaign_media=camp_media_list,
        rewards=reward_list_raw, reward_media=reward_media_list,
    )
    
        # ✅ async embedding
    if background_tasks:
        background_tasks.add_task(generate_post_embedding, post.id)

    return post
    

@router.put("/{post_id}/with-campaigns", response_model=schema.PostOut)
async def update(
    post_id: UUID,
    post_data: Union[str, None] = Form(None),
    media: Union[List[UploadFile], UploadFile, None] = File(None),              
    campaigns: Union[str, None] = Form(None),                                 
    campaign_media: Union[List[UploadFile], UploadFile, None] = File(None),
    rewards: Union[str, None] = Form(None),                                 
    reward_media: Union[List[UploadFile], UploadFile, None] = File(None),          
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
    media_manifest: Union[str, None] = Form(None),         
    media_reorder: Union[str, None] = Form(None),   
    background_tasks: BackgroundTasks = None,
):
    # --- parse post_data ---
    post_upd = None
    if post_data:
        try:
            post_upd = schema.PostUpdate(**json.loads(post_data))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid post_data")

    # --- normalize media fields ---
    post_media_list: Optional[List[UploadFile]] = None
    if media is not None:
        post_media_list = media if isinstance(media, list) else [media]

    camp_media_list: Optional[List[UploadFile]] = None
    if campaign_media is not None:
        camp_media_list = campaign_media if isinstance(campaign_media, list) else [campaign_media]

    reward_media_list: Optional[List[UploadFile]] = None
    if reward_media is not None:
        reward_media_list = reward_media if isinstance(reward_media, list) else [reward_media]

    # --- parse campaigns manifest (list[dict]) ---
    camp_payload = None
    if campaigns:
        parsed = json.loads(campaigns)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid campaigns payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid campaigns payload")
        camp_payload = parsed

    reward_payload = None
    if rewards:
        parsed = json.loads(rewards)
        if not isinstance(parsed, list): raise HTTPException(status_code=400, detail="Invalid rewards payload")
        for it in parsed:
            if not isinstance(it, dict) or "display_order" not in it: raise HTTPException(status_code=400, detail="Invalid rewards payload")
        reward_payload = parsed

    post_media_list = media if isinstance(media, list) else ([media] if media else None)
    media_manifest_parsed = json.loads(media_manifest) if media_manifest else None
    reorder_list = json.loads(media_reorder) if media_reorder else None

    # --- call service ---
    post = await service.update_post(
        db=db,
        post_id=post_id,
        clerk_id=clerk_id,
        post_data=post_upd,
        post_media=post_media_list,    
        campaigns_payload=camp_payload,  
        campaign_media=camp_media_list,
        rewards_payload=reward_payload,  
        reward_media=reward_media_list,
        post_media_manifest=media_manifest_parsed,           
        post_media_reorder=reorder_list, 
    )
    # ✅ ถ้ามี post_data แปลว่า content อาจเปลี่ยน → regenerate embedding
    if background_tasks and post_data:
        background_tasks.add_task(generate_post_embedding, post_id)

    return post
    
@router.put("/{post_id}/status", response_model=schema.PostOut)
def update_post_status(
    post_id: UUID,
    status: schema.PostStatus = Query(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
): 
    try:
        clerk_id = current_user["sub"]
        service.verify_post_owner(db, post_id, clerk_id)
        return service.change_post_status(db, post_id, status)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

  
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


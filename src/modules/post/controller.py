from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional, Union
import json
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from src.modules.campaign import schema as camp_schema, service as camp_service
from fastapi import Form 

router = APIRouter(prefix="/post", tags=["Post"])

@router.get("/", response_model=list[schema.PostOut])
def list_posts(db: Session = Depends(get_db)):
    return service.list_posts(db)

@router.get("/{post_id}", response_model=schema.PostOut)
def get_post(post_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.get_post(db, post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{post_id}", response_model=schema.PostOut)
def delete(post_id: UUID,clerk_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        service.verify_post_owner(db, post_id, clerk_id)
        return service.delete_post(db, post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/with-campaigns", response_model=schema.PostOut)
async def create_with_campaigns(
    post_data: str = Form(...),
    images: Union[List[UploadFile], UploadFile, None] = File(None),
    campaigns: Union[str, None] = Form(None),                                  
    campaign_images: Union[List[UploadFile], UploadFile, None] = File(None),    
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
):
    # print("post_images:", len(images or []))
    # print("create_campaigns:", len(campaigns or []), "camp_files:", len(campaign_images or []))

    try:
        post_obj = schema.PostCreate(**json.loads(post_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid post_data")

    post_img_list: Optional[List[UploadFile]] = None
    if images is not None:
        post_img_list = images if isinstance(images, list) else [images]

    camp_list_raw: Optional[List[dict]] = None
    if campaigns:
        try:
            parsed = json.loads(campaigns)
            if not isinstance(parsed, list):
                raise ValueError
            for it in parsed:
                if not isinstance(it, dict) or "order" not in it:
                    raise ValueError
            camp_list_raw = parsed
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid campaigns payload")


    camp_img_list: Optional[List[UploadFile]] = None
    if campaign_images is not None:
        camp_img_list = campaign_images if isinstance(campaign_images, list) else [campaign_images]

    if camp_list_raw is not None:
        if not camp_img_list or len(camp_img_list) != len(camp_list_raw):
            raise HTTPException(status_code=400, detail="campaign_images must match campaigns count (1:1).")

    return await service.create_post(
        db=db,
        clerk_id=clerk_id,
        post_data=post_obj,
        post_images=post_img_list,        
        campaigns=camp_list_raw,              
        campaign_images=camp_img_list,
    )

@router.put("/{post_id}/with-campaigns", response_model=schema.PostOut)
async def update_with_campaigns(
    post_id: UUID,
    post_data: Union[str, None] = Form(None),
    images: Union[List[UploadFile], UploadFile, None] = File(None),              
    campaigns: Union[str, None] = Form(None),                                 
    campaign_images: Union[List[UploadFile], UploadFile, None] = File(None),     
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
):
    # --- parse post_data ---
    post_upd = None
    if post_data:
        try:
            post_upd = schema.PostUpdate(**json.loads(post_data))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid post_data")

    # --- normalize images fields ---
    post_img_list: Optional[List[UploadFile]] = None
    if images is not None:
        post_img_list = images if isinstance(images, list) else [images]

    camp_img_list: Optional[List[UploadFile]] = None
    if campaign_images is not None:
        camp_img_list = campaign_images if isinstance(campaign_images, list) else [campaign_images]

    # --- parse campaigns manifest (list[dict]) ---
    camp_payload: Optional[List[dict]] = None
    if campaigns:
        try:
            parsed = json.loads(campaigns)
            if not isinstance(parsed, list):
                raise ValueError
            for it in parsed:
                if not isinstance(it, dict) or "order" not in it:
                    raise ValueError
            camp_payload = parsed
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid campaigns payload")

    # --- call service ---
    return await service.update_post(
        db=db,
        post_id=post_id,
        clerk_id=clerk_id,
        post_data=post_upd,
        post_images=post_img_list,    
        campaigns_payload=camp_payload,  
        campaign_images=camp_img_list,
    )
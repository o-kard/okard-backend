# modules/user/controller.py
import json
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from . import schema, service
from src.modules.auth import get_current_user
from src.database.db import get_db
from src.modules.media.schema import MediaOut
from src.modules.media.service import create_media_from_upload, delete_media
from src.modules.common.clerk_helper import update_clerk_user_password
from src.modules.creator.schema import CreatorUpdate

router = APIRouter(prefix="/user", tags=["user"])

@router.post("", response_model=schema.UserResponse)
async def create_user(
    data: str = Form(...), 
    media: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    password: Optional[str] = Form(None),
    payload: dict = Depends(get_current_user),
):
    try:
        user_obj = schema.UserCreate(**json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {str(e)}")

    clerk_id = payload["sub"]
    user_obj.clerk_id = clerk_id
    
    # Update password if provided
    if password:
        try:
            await run_in_threadpool(update_clerk_user_password, clerk_id, password)
        except Exception as e:
            print(f"Failed to set password: {e}")
            raise HTTPException(status_code=500, detail="Failed to set password")

    user_response = await service.create_user_from_clerk(db, user_obj)
    if media:
        media_response = await create_media_from_upload(
            db, 
            file=media, 
            clerk_id=user_response.clerk_id
        )
        
    return user_response

@router.put("/update", response_model=schema.UserResponse)
async def update_user(
    data: str = Form(...), 
    media: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
):
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid JSON format: {str(e)}. Please check your JSON syntax."
        )

    try:
        user_obj = schema.UserUpdate(**parsed_data['user'])
        creator_obj = CreatorUpdate(**parsed_data['creator'])
        remove_image = user_obj.remove_image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {str(e)}")
    
    clerk_id = payload["sub"]
    user_response = await service.update_profile(db, clerk_id, user_obj, creator_obj)
    if media:
        await create_media_from_upload(
            db, 
            file=media,
            clerk_id=clerk_id
        )
    elif remove_image and user_response.media:
        delete_media(db, user_response.media.id)
        
    return user_response

@router.get("/list", response_model=list[schema.UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = await service.list_users(db)
    return users

@router.get("/{id}", response_model=schema.UserResponse)
async def get_user_by_id(id: UUID, db: Session = Depends(get_db)):
    user = await service.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/exists/{clerk_id}", response_model=schema.UserExistsResponse)
async def user_exists(clerk_id: str, db: Session = Depends(get_db)):
    return {"exists": await service.get_user_by_clerk_id(db, clerk_id) is not None}

@router.get("", response_model=schema.UserResponse)
async def get_me(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clerk_id = payload["sub"]

    user = await service.get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=401)

    return user

@router.delete("/delete/{user_id}", response_model=schema.UserResponse)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user_response = service.delete_user(db, user_id)
    if not user_response:
        raise HTTPException(status_code=404, detail="User not found")
    return user_response

@router.put("/{user_id}/suspend", response_model=schema.UserResponse)
async def suspend_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = await service.suspend_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/activate", response_model=schema.UserResponse)
async def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = await service.activate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
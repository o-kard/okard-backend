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
from src.modules.image.schema import ImageOut
from src.modules.image.service import create_image_from_upload, delete_image
from src.modules.common.clerk_helper import update_clerk_user_password

router = APIRouter(prefix="/user", tags=["user"])

@router.post("", response_model=schema.UserResponse)
async def create_user(
    data: str = Form(...), 
    image: Optional[UploadFile] = File(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
):
    try:
        user_obj = schema.UserCreate(**json.loads(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user data")

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
    if image:
        image_response = await create_image_from_upload(
            db, 
            file=image, 
            clerk_id=clerk_id
        )
        
    return user_response

@router.put("/update/{user_id}", response_model=schema.UserResponse)
async def update_user(
    user_id: UUID,
    data: str = Form(...), 
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        user_obj = schema.UserUpdate(**json.loads(data))
        remove_image = user_obj.remove_image
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    user_response = await service.update_user_from_clerk(db, user_id, user_obj)
    if image:
        await create_image_from_upload(
            db, 
            file=image,
            clerk_id=user_response.clerk_id
        )
    elif remove_image and user_response.image:
        await delete_image(db, user_response.image.id)
        
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
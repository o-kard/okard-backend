# modules/user/controller.py
import json
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import schema, service
from src.database.db import get_db
from src.modules.image.schema import ImageOut
from src.modules.image.service import create_image_from_upload, delete_image

router = APIRouter(prefix="/user", tags=["user"])

@router.post("", response_model=schema.UserOut)
async def create_user(
    data: str = Form(...), 
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        user_obj = schema.UserCreate(**json.loads(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    user_response = await service.create_user_from_clerk(db, user_obj)
    if image:
        image_response = await create_image_from_upload(
            db, 
            file=image, 
            clerk_id=user_response.clerk_id
        )
        
    return user_response

@router.put("/update/{user_id}", response_model=schema.UserOut)
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
    
    user_response = service.update_user_from_clerk(db, user_id, user_obj)
    if image:
        await create_image_from_upload(
            db, 
            file=image,
            clerk_id=user_response.clerk_id
        )
    elif remove_image and user_response.image:
        delete_image(db, user_response.image.id)
        
    return user_response

@router.get("/{clerk_id}", response_model=schema.UserOut)
def get_user_by_clerk_id(clerk_id: str, db: Session = Depends(get_db)):
    user = service.get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/exists/{clerk_id}", response_model=schema.ExistsOut)
def user_exists(clerk_id: str, db: Session = Depends(get_db)):
    return {"exists": service.get_user_by_clerk_id(db, clerk_id) is not None}
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Union
from .schema import PostCreate
import json
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from fastapi import Query 

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

@router.post("/", response_model=schema.PostOut)
def create(post: schema.PostCreate, db: Session = Depends(get_db)):
    return service.create_post(db, post)

@router.put("/{post_id}", response_model=schema.PostOut)
def update(post_id: UUID, post: schema.PostUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_post(db, post_id, post)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{post_id}", response_model=schema.PostOut)
def delete(post_id: UUID,clerk_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        service.verify_post_owner(db, post_id, clerk_id)
        return service.delete_post(db, post_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("/with-images", response_model=schema.PostOut)
async def create_with_images(
    post_data: str = Form(...),
    images: Union[List[UploadFile], UploadFile] = File(...),
    clerk_id: str = Query(...), 
    db: Session = Depends(get_db)
):
    try:
        data_dict = json.loads(post_data)
        post_obj = PostCreate(**data_dict)
    except Exception as e:
        print("JSON parse error:", str(e))
        raise HTTPException(status_code=400, detail=f"Invalid post_data: {str(e)}")

    if isinstance(images, UploadFile):
        images = [images]

    return await service.create_post_by_clerk_id_with_images(db, post_obj, clerk_id, images)

@router.put("/{post_id}/with-images", response_model=schema.PostOut)
async def update_with_images(
    post_id: UUID,
    post_data: str = Form(...),
    images: Union[List[UploadFile], UploadFile] = File(...),
    clerk_id: str = Query(...), 
    db: Session = Depends(get_db)
):
    try:
        data_dict = json.loads(post_data)
        post_obj = schema.PostUpdate(**data_dict)
    except Exception as e:
        print("JSON parse error:", str(e))
        raise HTTPException(status_code=400, detail=f"Invalid post_data: {str(e)}")

    if isinstance(images, UploadFile):
        images = [images]

    try:
        service.verify_post_owner(db, post_id, clerk_id)
        return await service.update_post_with_images(db, post_id, post_obj, images)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

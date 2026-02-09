# modules/user/service.py
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from . import repo, schema

async def create_user_from_clerk(
    db: Session, 
    user_data: schema.UserCreate,
):
    return repo.create_user(db, user_data)

async def get_user_by_clerk_id(db: Session, clerk_id: str):
    return repo.get_user_by_clerk_id(db, clerk_id)

async def update_user_from_clerk(db: Session, user_id, user_data: schema.UserUpdate):
    return repo.update_user(db, user_id, user_data)

async def list_users(db: Session):
    return repo.list_users(db)
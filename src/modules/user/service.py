# modules/user/service.py
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from . import repo, schema
from src.modules.creator import repo as creator_repo
from src.modules.creator.schema import CreatorUpdate
from src.modules.common.enums import CampaignState
from uuid import UUID
from fastapi import HTTPException
from src.modules.common.enums import UserStatus

async def create_user_from_clerk(
    db: Session, 
    user_data: schema.UserCreate,
):
    return repo.create_user(db, user_data)

async def get_user_by_clerk_id(db: Session, clerk_id: str):
    return repo.get_user_by_clerk_id(db, clerk_id)

async def update_profile(
    db: Session, 
    clerk_id: str, 
    user_data: schema.UserUpdate, 
    creator_data: CreatorUpdate | None = None
):
    # 1. Update User
    user = repo.update_user(db, clerk_id, user_data)
    
    # 2. Update Creator (if data provided and user has creator profile)
    if creator_data:
        creator = creator_repo.get_creator_by_user_id(db, user.id)
        if creator:
            creator_repo.update_creator(db, creator.id, creator_data)
            
    return user

async def list_users(db: Session):
    return repo.list_users(db)

async def get_user_by_id(db: Session, user_id: UUID):
    return repo.get_user_by_id(db, user_id)

def delete_user(db: Session, user_id: UUID):
    return repo.delete_user(db, user_id)

async def suspend_user(db: Session, user_id: UUID):
    user = await get_user_by_id(db, user_id)
    if user:
        # Suspend all user's campaigns
        for campaign in user.campaigns:
            campaign.state = CampaignState.suspend
        return repo.suspend_user(db, user)
    return None

async def activate_user(db: Session, user_id: UUID):
    user = await get_user_by_id(db, user_id)
    if user:
        return repo.activate_user(db, user)
    return None

async def check_user_active(db: Session, clerk_id: str):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status == UserStatus.suspended:
        raise HTTPException(status_code=403, detail="User is suspended and cannot perform this action")
    return user
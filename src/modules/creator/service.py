from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from . import repo
from .schema import CreatorCreate, CreatorUpdate

async def create_creator(db: Session, creator_data: CreatorCreate, clerk_id: str):
    """Create a new creator profile"""
    print("create_creator", clerk_id)
    user = await get_user_by_clerk_id(db, clerk_id)
    print("user", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if creator profile already exists
    existing_creator = repo.get_creator_by_user_id(db, user.id)
    if existing_creator:
        raise HTTPException(status_code=400, detail="Creator profile already exists")
    
    return repo.create_creator(db, creator_data, user.id)

async def get_creator_by_id(db: Session, creator_id: UUID):
    """Get creator by ID"""
    return repo.get_creator_by_id(db, creator_id)

async def get_creator_by_clerk_id(db: Session, clerk_id: str):
    """Get creator by clerk_id"""
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        return None
    return repo.get_creator_by_user_id(db, user.id)

async def update_creator(db: Session, creator_id: UUID, creator_data: CreatorUpdate, clerk_id: str):
    """Update creator profile"""
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    creator = repo.get_creator_by_id(db, creator_id)
    if not creator:
        raise ValueError("Creator not found")
    
    # Check if the user owns this creator profile
    if creator.user_id != user.id:
        raise PermissionError("You don't have permission to update this creator profile")
    
    return repo.update_creator(db, creator_id, creator_data)

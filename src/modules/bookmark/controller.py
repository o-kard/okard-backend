from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict

from src.database.db import get_db
from src.modules.auth import get_current_user
from src.modules.user.schema import UserPublicResponse
from src.modules.bookmark import service as bookmark_service
from src.modules.campaign.schema import CampaignOut, CampaignSummaryOut
from src.modules.user import service as user_service

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

@router.post("/{campaign_id}", response_model=Dict[str, bool])
async def toggle_bookmark(
    campaign_id: UUID,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clerk_id = payload["sub"]

    user = await user_service.get_user_by_clerk_id(db, clerk_id)
    
    return bookmark_service.toggle_bookmark(db, user.id, campaign_id)

@router.get("/", response_model=List[CampaignSummaryOut])
async def get_user_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clerk_id = payload["sub"]

    user = await user_service.get_user_by_clerk_id(db, clerk_id)

    bookmarks = bookmark_service.get_bookmarks(db, user.id, skip, limit)
    # Return the campaign objects of these bookmarks
    return [b.campaign for b in bookmarks]

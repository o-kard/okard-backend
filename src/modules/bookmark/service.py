from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from typing import List

from src.modules.bookmark import repo as bookmark_repo
from src.modules.bookmark.model import Bookmark
from src.modules.campaign import service as campaign_service

def toggle_bookmark(db: Session, user_id: UUID, campaign_id: UUID) -> dict:
    # verify campaign exists
    campaign = campaign_service.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    existing = bookmark_repo.get_bookmark(db, user_id, campaign_id)
    if existing:
        bookmark_repo.delete_bookmark(db, user_id, campaign_id)
        db.commit()
        return {"bookmarked": False}
    else:
        bookmark_repo.create_bookmark(db, user_id, campaign_id)
        db.commit()
        return {"bookmarked": True}

def get_bookmarks(db: Session, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Bookmark]:
    return bookmark_repo.get_user_bookmarks(db, user_id, skip, limit)

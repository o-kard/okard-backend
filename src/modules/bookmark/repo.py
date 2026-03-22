from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import delete, and_
from uuid import UUID
from typing import List, Optional

from src.modules.bookmark.model import Bookmark

def get_bookmark(db: Session, user_id: UUID, campaign_id: UUID) -> Optional[Bookmark]:
    query = select(Bookmark).where(
        and_(Bookmark.user_id == user_id, Bookmark.campaign_id == campaign_id)
    )
    result = db.execute(query).scalar_one_or_none()
    return result

def get_user_bookmarks(db: Session, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Bookmark]:
    query = select(Bookmark).where(Bookmark.user_id == user_id).offset(skip).limit(limit)
    result = db.execute(query).scalars().all()
    return list(result)

def get_user_bookmarked_campaign_ids(db: Session, user_id: UUID) -> set[UUID]:
    query = select(Bookmark.campaign_id).where(Bookmark.user_id == user_id)
    result = db.execute(query).scalars().all()
    return set(result)
    
def create_bookmark(db: Session, user_id: UUID, campaign_id: UUID) -> Bookmark:
    item = Bookmark(user_id=user_id, campaign_id=campaign_id)
    db.add(item)
    db.flush()
    return item

def delete_bookmark(db: Session, user_id: UUID, campaign_id: UUID) -> bool:
    query = delete(Bookmark).where(
        and_(Bookmark.user_id == user_id, Bookmark.campaign_id == campaign_id)
    )
    result = db.execute(query)
    db.flush()
    return result.rowcount > 0

def hydrate_campaign_bookmarks(db: Session, campaigns: List[any], user_id: UUID | None):
    if not user_id or not campaigns:
        for c in campaigns:
            if isinstance(c, dict):
                campaign_obj = c.get("campaign")
                if campaign_obj:
                    campaign_obj.is_bookmarked = False
            else:
                c.is_bookmarked = False
        return

    campaign_list = []
    campaign_ids = []
    for c in campaigns:
        if isinstance(c, dict) and "campaign" in c:
            obj = c["campaign"]
        else:
            obj = c
        campaign_list.append(obj)
        campaign_ids.append(obj.id)

    bookmarked_ids = db.execute(
        select(Bookmark.campaign_id)
        .where(Bookmark.user_id == user_id, Bookmark.campaign_id.in_(campaign_ids))
    ).scalars().all()
    bookmarked_set = set(bookmarked_ids)

    for obj in campaign_list:
        obj.is_bookmarked = obj.id in bookmarked_set

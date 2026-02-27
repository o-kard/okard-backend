from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from typing import List

from src.modules.bookmark import repo as bookmark_repo
from src.modules.bookmark.model import Bookmark
from src.modules.post import service as post_service

def toggle_bookmark(db: Session, user_id: UUID, post_id: UUID) -> dict:
    # verify post exists
    post = post_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = bookmark_repo.get_bookmark(db, user_id, post_id)
    if existing:
        bookmark_repo.delete_bookmark(db, user_id, post_id)
        db.commit()
        return {"bookmarked": False}
    else:
        bookmark_repo.create_bookmark(db, user_id, post_id)
        db.commit()
        return {"bookmarked": True}

def get_bookmarks(db: Session, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Bookmark]:
    return bookmark_repo.get_user_bookmarks(db, user_id, skip, limit)

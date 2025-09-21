from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.repo import get_user_by_clerk_id
from . import repo
from .schema import CommentCreate

def add_comment(db: Session, comment_data: CommentCreate, clerk_id: str):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.create_comment(db, comment_data, user.id)

def list_comments(db: Session, post_id: UUID, clerk_id: str | None = None):
    viewer = get_user_by_clerk_id(db, clerk_id) if clerk_id else None
    viewer_id = viewer.id if viewer else None
    return repo.lists_comments(db, post_id, viewer_id)

def like(db: Session, comment_id: UUID, clerk_id: str):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.like_comment(db, comment_id, user.id)

def unlike(db: Session, comment_id: UUID, clerk_id: str):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.unlike_comment(db, comment_id, user.id)

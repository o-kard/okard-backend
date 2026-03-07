from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from src.modules.notification import service as notification_service, schema as notification_schema
from src.modules.common.enums import NotificationType
from src.modules.post import repo as post_repo
from . import repo
from .schema import CommentCreate

async def add_comment(db: Session, comment_data: CommentCreate, clerk_id: str):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    comment = repo.create_comment(db, comment_data, user.id)
    
    post = post_repo.get_post(db, comment_data.post_id)
    if post and post.user_id != user.id:
        notif = notification_schema.NotificationCreate(
            user_id=post.user_id,
            actor_id=user.id,
            post_id=post.id,
            notification_title="New Comment",
            notification_message=f"{user.username or 'Someone'} commented on your post '{post.post_header}'",
            type=NotificationType.comment
        )
        await notification_service.create_notification(db, notif)
        
    return comment

async def list_comments(db: Session, post_id: UUID, clerk_id: str | None = None):
    viewer = await get_user_by_clerk_id(db, clerk_id) if clerk_id else None
    viewer_id = viewer.id if viewer else None
    return repo.lists_comments(db, post_id, viewer_id)

async def like(db: Session, comment_id: UUID, clerk_id: str):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.like_comment(db, comment_id, user.id)

async def unlike(db: Session, comment_id: UUID, clerk_id: str):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.unlike_comment(db, comment_id, user.id)

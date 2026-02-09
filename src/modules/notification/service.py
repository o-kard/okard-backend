from http.client import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from . import model, repo
from src.modules.user.service import get_user_by_clerk_id

from . import model, repo, schema

async def list_notifications(db: Session, clerk_id: str | None = None):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        return []
    return repo.list_notifications(db, user.id)

async def get_notification_or_404(db: Session, notification_id: UUID):
    notif = repo.get_notification(db, notification_id)
    if not notif:
        raise ValueError("Notification not found")
    return notif

async def create_notification(db: Session, notif_in: schema.NotificationCreate):
    db_notif = model.Notification(**notif_in.model_dump())
    return repo.create_notification(db, db_notif)

async def delete_notification(db: Session, notification_id: UUID):
    notif = await get_notification_or_404(db, notification_id)
    return repo.delete_notification(db, notif)


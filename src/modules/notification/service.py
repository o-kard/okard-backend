from http.client import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from . import model, repo

from . import model, repo, schema

def list_notifications(db: Session, user_id: UUID | None = None):
    return repo.list_notifications(db, user_id)

def get_notification_or_404(db: Session, notification_id: UUID):
    notif = repo.get_notification(db, notification_id)
    if not notif:
        raise ValueError("Notification not found")
    return notif

def create_notification(db: Session, notif_in: schema.NotificationCreate):
    db_notif = model.Notification(**notif_in.model_dump())
    return repo.create_notification(db, db_notif)

def delete_notification(db: Session, notification_id: UUID):
    notif = get_notification_or_404(db, notification_id)
    return repo.delete_notification(db, notif)


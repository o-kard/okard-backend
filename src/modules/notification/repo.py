from sqlalchemy.orm import Session, joinedload
from . import model, schema
from uuid import UUID

def list_notifications(db: Session, user_id: UUID | None = None):
    query = db.query(model.Notification)
    if user_id:
        query = query.filter(model.Notification.user_id == user_id)
    return query.order_by(model.Notification.created_at.desc()).all()

def get_notification(db: Session, notification_id: UUID):
    return db.query(model.Notification).filter(model.Notification.id == notification_id).first()

def create_notification(db: Session, notification: model.Notification):
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def delete_notification(db: Session, db_notification: model.Notification):
    db.delete(db_notification)
    db.commit()
    return db_notification


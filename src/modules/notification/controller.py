from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from fastapi import Form

router = APIRouter(prefix="/notification", tags=["Notification"])

@router.get("", response_model=list[schema.NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    user_id: UUID | None = None
):
    return service.list_notifications(db, user_id)

@router.get("/{notification_id}", response_model=schema.NotificationOut)
def get_notification(notification_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.get_notification_or_404(db, notification_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("", response_model=schema.NotificationOut)
def create_notification(notif_in: schema.NotificationCreate, db: Session = Depends(get_db)):
    return service.create_notification(db, notif_in)

@router.delete("/{notification_id}", response_model=schema.NotificationOut)
def delete_notification(notification_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.delete_notification(db, notification_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")


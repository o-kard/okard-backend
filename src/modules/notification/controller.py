from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import schema, service
from fastapi import Form, Query

router = APIRouter(prefix="/notification", tags=["Notification"])

@router.get("", response_model=list[schema.NotificationOut])
async def list_notifications(
    db: Session = Depends(get_db),
    clerk_id: str = Query(...)
):
    return await service.list_notifications(db, clerk_id)

@router.get("/{notification_id}", response_model=schema.NotificationOut)
async def get_notification(notification_id: UUID, db: Session = Depends(get_db)):
    try:
        return await service.get_notification_or_404(db, notification_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")

@router.post("", response_model=schema.NotificationOut)
async def create_notification(notif_in: schema.NotificationCreate, db: Session = Depends(get_db)):
    return await service.create_notification(db, notif_in)

@router.delete("/{notification_id}", response_model=schema.NotificationOut)
async def delete_notification(notification_id: UUID, db: Session = Depends(get_db)):
    try:
        return await service.delete_notification(db, notification_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found")


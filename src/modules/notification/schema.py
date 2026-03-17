from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from src.modules.common.enums import NotificationType

class NotificationBase(BaseModel):
    campaign_id: Optional[UUID] = None
    user_id: UUID
    actor_id: Optional[UUID] = None
    notification_title: str 
    notification_message: str
    type: NotificationType

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    pass

class NotificationOut(NotificationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
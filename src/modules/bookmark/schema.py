from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class BookmarkCreate(BaseModel):
    campaign_id: UUID

class BookmarkOut(BaseModel):
    id: UUID
    user_id: UUID
    campaign_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

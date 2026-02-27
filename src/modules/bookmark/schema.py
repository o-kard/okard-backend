from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class BookmarkCreate(BaseModel):
    post_id: UUID

class BookmarkOut(BaseModel):
    id: UUID
    user_id: UUID
    post_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

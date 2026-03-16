from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.media.schema import MediaOut

class ProgressBase(BaseModel):
    progress_header: Optional[str] = None
    progress_description: Optional[str] = None

class ProgressCreate(ProgressBase):
    campaign_id: UUID

class ProgressUpdate(ProgressBase):
    campaign_id: Optional[UUID] = None

class ProgressOut(ProgressBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    media: List[MediaOut] = []
    class Config:
        from_attributes = True

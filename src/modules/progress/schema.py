from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.image.schema import ImageOut

class ProgressBase(BaseModel):
    progress_header: Optional[str] = None
    progress_description: Optional[str] = None

class ProgressCreate(ProgressBase):
    post_id: UUID

class ProgressUpdate(ProgressBase):
    post_id: Optional[UUID] = None

class ProgressOut(ProgressBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[ImageOut] = []
    class Config:
        from_attributes = True

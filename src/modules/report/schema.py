from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.common.enums import ReportType, ReportStatus
from src.modules.image.schema import ImageOut

class ReportBase(BaseModel):
    post_id: Optional[UUID] = None
    type: ReportType
    header: Optional[str] = None
    description: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportOut(ReportBase):
    id: UUID
    reporter_id: UUID
    status: ReportStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    files: List[ImageOut] = []
    
    class Config:
        orm_mode = True

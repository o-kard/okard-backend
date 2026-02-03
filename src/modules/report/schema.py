from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.common.enums import ReportType, ReportStatus
from src.modules.media.schema import MediaOut

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
    files: List[MediaOut] = []
    
    class Config:
        from_attributes = True

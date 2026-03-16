from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.media.schema import MediaOut

class InformationBase(BaseModel):
    information_header: Optional[str] = None    
    information_description: Optional[str] = None 
    display_order: Optional[int] = 0

class InformationCreate(InformationBase):
    campaign_id: UUID

class InformationUpdate(InformationBase):
    campaign_id: Optional[UUID] = None             

class InformationOut(InformationBase):
    id: UUID
    created_at: datetime
    media: List[MediaOut] = []              
    class Config:
        from_attributes = True

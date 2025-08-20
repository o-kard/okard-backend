from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.image.schema import ImageOut

class CampaignBase(BaseModel):
    campaign_header: Optional[str] = None    
    campaign_description: Optional[str] = None 
    order: int

class CampaignCreate(CampaignBase):
    post_id: UUID

class CampaignUpdate(CampaignBase):
    post_id: Optional[UUID] = None             

class CampaignOut(CampaignBase):
    id: UUID
    created_at: datetime
    images: List[ImageOut] = []              
    class Config:
        orm_mode = True

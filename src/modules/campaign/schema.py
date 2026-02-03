from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.media.schema import MediaOut

class CampaignBase(BaseModel):
    campaign_header: Optional[str] = None    
    campaign_description: Optional[str] = None 
    display_order: Optional[int] = 0

class CampaignCreate(CampaignBase):
    post_id: UUID

class CampaignUpdate(CampaignBase):
    post_id: Optional[UUID] = None             

class CampaignOut(CampaignBase):
    id: UUID
    created_at: datetime
    media: List[MediaOut] = []              
    class Config:
        from_attributes = True

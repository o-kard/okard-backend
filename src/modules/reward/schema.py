from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.media.schema import MediaOut

class RewardBase(BaseModel):
    reward_header: Optional[str] = None    
    reward_description: Optional[str] = None 
    display_order: Optional[int] = 0
    reward_amount: int
    backup_amount: int

class RewardCreate(RewardBase):
    campaign_id: UUID

class RewardUpdate(BaseModel):
    reward_header: Optional[str] = None    
    reward_description: Optional[str] = None 
    display_order: Optional[int] = None
    reward_amount: Optional[int] = None
    backup_amount: Optional[int] = None
    campaign_id: Optional[UUID] = None

class RewardOut(RewardBase):
    id: UUID
    created_at: datetime
    media: List[MediaOut] = []              
    class Config:
        from_attributes = True

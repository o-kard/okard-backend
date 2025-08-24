from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.modules.image.schema import ImageOut

class RewardBase(BaseModel):
    reward_header: Optional[str] = None    
    reward_description: Optional[str] = None 
    order: int
    reward_amount: int
    backup_amount: int

class RewardCreate(RewardBase):
    post_id: UUID

class RewardUpdate(RewardBase):
    post_id: Optional[UUID] = None             

class RewardOut(RewardBase):
    id: UUID
    created_at: datetime
    image: List[ImageOut] = []              
    class Config:
        orm_mode = True

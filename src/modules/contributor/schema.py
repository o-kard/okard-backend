from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


from src.modules.campaign.schema import CampaignSummaryOut

class ContributorBase(BaseModel):
    user_id: UUID
    campaign_id: UUID
    total_amount: int = 0

class ContributorCreate(ContributorBase):
    pass

class ContributorUpdate(BaseModel):
    total_amount: Optional[int] = None

class ContributorOut(ContributorBase):
    id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True

class ContributorWithCampaignOut(ContributorOut):
    campaign: CampaignSummaryOut


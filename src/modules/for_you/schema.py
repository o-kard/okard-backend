from pydantic import BaseModel
from uuid import UUID
from typing import List
from src.modules.home.schema import CampaignSummaryOut

class ForYouCampaign(BaseModel):
    campaign: CampaignSummaryOut
    score: float

class ForYouResponse(BaseModel):
    user_id: UUID | None
    campaigns: list[ForYouCampaign]

from pydantic import BaseModel
from uuid import UUID
from typing import List

from src.modules.campaign.schema import CampaignSummaryOut

class RecommendedCampaign(BaseModel):
    campaign_id: UUID
    score: float
    campaign: CampaignSummaryOut

class CampaignRecommendResponse(BaseModel):
    source_campaign_id: UUID
    recommendations: List[RecommendedCampaign]

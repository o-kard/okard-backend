from pydantic import BaseModel
from uuid import UUID
from typing import List

class RecommendedCampaign(BaseModel):
    campaign_id: UUID
    score: float

class CampaignRecommendResponse(BaseModel):
    source_campaign_id: UUID
    recommendations: List[RecommendedCampaign]

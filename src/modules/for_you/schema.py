from pydantic import BaseModel
from uuid import UUID
from typing import List
from src.modules.home.schema import PostSummaryOut

class ForYouCampaign(BaseModel):
    campaign: PostSummaryOut
    score: float

class ForYouResponse(BaseModel):
    user_id: UUID
    campaigns: list[ForYouCampaign]

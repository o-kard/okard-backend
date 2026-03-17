# src/modules/home/schema.py
from pydantic import BaseModel
from typing import List, Optional
from src.modules.campaign.schema import CampaignSummaryOut

class HomeCampaignOut(CampaignSummaryOut):
    pass

class CategoryStat(BaseModel):
    category: str
    total_projects: int
    funded_projects: int
    total_raised: float
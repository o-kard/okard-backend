from pydantic import BaseModel
from uuid import UUID
from datetime import date

class UserDashboardSummary(BaseModel):
    user_id: UUID
    campaign_count: int
    unique_investor_count: int
    total_raised: int
    hit_goal_campaign_count: int

class CampaignProgress(BaseModel):
    campaign_id: UUID
    title: str
    goal_amount: int
    current_amount: int
    progress_pct: float
    investor_count: int
    hit_goal: bool

class PaymentDailyStat(BaseModel):
    date: date
    total_amount: int

class InvestorCountryStat(BaseModel):
    country: str
    invest_count: int

class TrendingCampaign(BaseModel):
    campaign_id: UUID
    campaign_header: str
    donate_count: int

    class Config:
        from_attributes = True

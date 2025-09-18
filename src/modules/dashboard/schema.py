from pydantic import BaseModel
from uuid import UUID

class UserDashboardSummary(BaseModel):
    user_id: UUID
    post_count: int
    unique_investor_count: int
    total_raised: int
    hit_goal_post_count: int

class PostProgress(BaseModel):
    post_id: UUID
    title: str
    goal_amount: int
    current_amount: int
    progress_pct: float
    investor_count: int
    hit_goal: bool

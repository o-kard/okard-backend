from pydantic import BaseModel, computed_field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from src.modules.reward.schema import RewardOut
from src.modules.common.enums import CampaignState, CampaignCategory
from src.modules.media.schema import MediaOut
from src.modules.information.schema import InformationOut
from src.modules.user.schema import UserPublicResponse

class AIPredictionOut(BaseModel):
    success_label: Optional[str] = None
    risk_label: Optional[str] = None
    days_to_state_label: Optional[str] = None
    goal_eval_label: Optional[str] = None
    stretch_label: Optional[str] = None

class CampaignBase(BaseModel):
    effective_start_from: Optional[datetime]
    effective_end_date: Optional[datetime]
    state: Optional[CampaignState]
    category: Optional[CampaignCategory]
    goal_amount: Optional[int] = 0
    current_amount: Optional[int] = 0
    campaign_header: str
    campaign_description: Optional[str] = None
    supporter: Optional[int] = 0

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    effective_start_from: Optional[datetime] = None
    effective_end_date: Optional[datetime] = None
    state: Optional[CampaignState] = None
    category: Optional[CampaignCategory] = None
    goal_amount: Optional[int] = None
    current_amount: Optional[int] = None
    campaign_header: Optional[str] = None
    campaign_description: Optional[str] = None
    supporter: Optional[int] = None

class CampaignOut(CampaignBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    media: List[MediaOut] = []
    informations: List[InformationOut] = []
    rewards: List[RewardOut] = []
    user: UserPublicResponse
    is_bookmarked: bool = False

    @computed_field
    @property
    def images(self) -> List[MediaOut]:
        return [m for m in self.media if not (m.media_type or "").startswith("video/")]

    @computed_field
    @property
    def video(self) -> Optional[MediaOut]:
        vids = [m for m in self.media if (m.media_type or "").startswith("video/")]
        return vids[0] if vids else None

    ai_label: Optional[AIPredictionOut] = None
    
    class Config:
        from_attributes = True
            
class CampaignSummaryOut(BaseModel):
    id: UUID
    user_id: UUID
    category: CampaignCategory

    campaign_header: str
    campaign_description: str | None

    goal_amount: int
    current_amount: int
    supporter: int

    effective_start_from: Optional[datetime] = None
    effective_end_date: Optional[datetime] = None

    @computed_field
    @property
    def supporters(self) -> int:
        return self.supporter

    media: List[MediaOut]
    user: UserPublicResponse
    state: Optional[CampaignState]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_bookmarked: bool = False
    
    @computed_field
    @property
    def progress(self) -> int:
        if self.goal_amount:
            return int((self.current_amount / self.goal_amount) * 100)
        return 0

    @computed_field
    @property
    def images(self) -> List[MediaOut]:
        return [m for m in self.media if not (m.media_type or "").startswith("video/")]

    @computed_field
    @property
    def video(self) -> Optional[MediaOut]:
        vids = [m for m in self.media if (m.media_type or "").startswith("video/")]
        return vids[0] if vids else None

    ai_label: Optional[AIPredictionOut] = None

    class Config:
        from_attributes = True

class CitySupporterStat(BaseModel):
    city: str
    supporter: int

class CampaignCommunityOut(BaseModel):
    total_supporters: int
    top_cities: List[CitySupporterStat]

from pydantic import BaseModel, computed_field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from src.modules.reward.schema import RewardOut
from src.modules.common.enums import PostState, PostStatus, PostCategory
from src.modules.media.schema import MediaOut
from src.modules.campaign.schema import CampaignOut
from src.modules.user.schema import UserPublicResponse

class PostBase(BaseModel):
    effective_start_from: Optional[datetime]
    effective_end_date: Optional[datetime]
    state: Optional[PostState]
    status: Optional[PostStatus]
    category: Optional[PostCategory]
    goal_amount: Optional[int] = 0
    current_amount: Optional[int] = 0
    post_header: str
    post_description: Optional[str] = None
    supporter: Optional[int] = 0

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    effective_start_from: Optional[datetime] = None
    effective_end_date: Optional[datetime] = None
    state: Optional[PostState] = None
    status: Optional[PostStatus] = None
    category: Optional[PostCategory] = None
    goal_amount: Optional[int] = None
    current_amount: Optional[int] = None
    post_header: Optional[str] = None
    post_description: Optional[str] = None
    supporter: Optional[int] = None

class PostOut(PostBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    media: List[MediaOut] = []
    campaigns: List[CampaignOut] = []
    rewards: List[RewardOut] = []
    user: UserPublicResponse

    @computed_field
    @property
    def images(self) -> List[MediaOut]:
        return [m for m in self.media if not (m.media_type or "").startswith("video/")]

    @computed_field
    @property
    def video(self) -> Optional[MediaOut]:
        vids = [m for m in self.media if (m.media_type or "").startswith("video/")]
        return vids[0] if vids else None
    
    class Config:
        from_attributes = True
            
class PostSummaryOut(BaseModel):
    id: UUID
    user_id: UUID
    category: PostCategory

    post_header: str
    post_description: str | None

    goal_amount: int
    current_amount: int
    supporter: int

    media: List[MediaOut]
    user: UserPublicResponse
    state: Optional[PostState]
    status: Optional[PostStatus]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
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

    class Config:
        from_attributes = True

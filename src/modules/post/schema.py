from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from .model import PostState, PostStatus, PostCategory
from src.modules.image.schema import ImageOut

class PostBase(BaseModel):
    effective_start_from: Optional[datetime]
    effective_end_date: Optional[datetime]
    state: Optional[PostState]
    status: Optional[PostStatus]
    category: Optional[PostCategory]
    goal_amount: int
    current_amount: int
    post_header: str
    post_description: Optional[str]
    supporter: int

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostOut(PostBase):
    id: UUID
    created_at: datetime
    images: List[ImageOut] = []

    class Config:
        orm_mode = True

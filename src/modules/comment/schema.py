from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from src.modules.user.schema import UserPublicResponse

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    campaign_id: UUID
    parent_id: Optional[UUID] = None

class CommentOut(CommentBase):
    id: UUID
    campaign_id: UUID
    parent_id: Optional[UUID]
    user_id: UUID
    likes: int
    created_at: datetime
    
    is_liked: Optional[bool] = None
    author: UserPublicResponse
    children: Optional[List["CommentOut"]] = None

    class Config:
        from_attributes = True
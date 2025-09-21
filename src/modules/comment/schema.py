from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from src.modules.user.schema import UserPublicOut

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: UUID
    parent_id: Optional[UUID] = None

class CommentOut(CommentBase):
    id: UUID
    post_id: UUID
    parent_id: Optional[UUID]
    user_id: UUID
    likes: int
    created_at: datetime
    
    is_liked: Optional[bool] = None
    author: UserPublicOut
    children: Optional[List["CommentOut"]] = None

    class Config:
        orm_mode = True
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class MediaBase(BaseModel):
    display_order: Optional[int] = None
    orig_name: Optional[str] = None
    media_type: Optional[str] = None
    file_size: Optional[int] = None
    thumbnail_path: Optional[str] = None

class MediaCreate(MediaBase):
    pass

class MediaUpdate(MediaBase):
    pass

class MediaOut(MediaBase):
    id: UUID
    path: str
    thumbnail_path: Optional[str] = None

    class Config:
        from_attributes = True
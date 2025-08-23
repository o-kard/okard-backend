from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ImageBase(BaseModel):
    order: Optional[int] = None
    post_id: Optional[UUID] = None  # Optional for post association
    user_id: Optional[UUID] = None  # Optional for user association
    orig_name: str
    media_type: str
    file_size: int

class ImageCreate(ImageBase):
    pass

class ImageUpdate(ImageBase):
    pass

class ImageOut(ImageBase):
    id: UUID
    path: str

    class Config:
        orm_mode = True

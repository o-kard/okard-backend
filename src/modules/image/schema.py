from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ImageBase(BaseModel):
    order: Optional[int]
    post_id: UUID
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

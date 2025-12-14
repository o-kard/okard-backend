from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ImageBase(BaseModel):
    display_order: Optional[int] = None
    orig_name: Optional[str] = None
    media_type: Optional[str] = None
    file_size: Optional[int] = None

class ImageCreate(ImageBase):
    pass

class ImageUpdate(ImageBase):
    pass

class ImageOut(ImageBase):
    id: UUID
    path: str

    class Config:
        orm_mode = True
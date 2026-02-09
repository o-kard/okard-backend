from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from src.modules.common.enums import StorageProvider, VerificationDocType

class CreatorVerificationDocBase(BaseModel):
    type: VerificationDocType
    storage_provider: StorageProvider = StorageProvider.local
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

class CreatorVerificationDocCreate(CreatorVerificationDocBase):
    creator_id: UUID
    file_path: str

class CreatorVerificationDocOut(CreatorVerificationDocBase):
    id: UUID
    creator_id: UUID
    file_path: str
    uploaded_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

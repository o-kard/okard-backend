from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

from src.modules.user.schema import UserPublicResponse
from src.modules.common.enums import VerificationStatus

class CreatorBase(BaseModel):
    bio: Optional[str] = None
    social_links: Optional[List[dict]] = None

class CreatorCreate(CreatorBase):
    pass

class CreatorUpdate(CreatorBase):
    pass
 
class CreatorOut(CreatorBase):
    id: UUID
    user_id: UUID
    campaign_number: int
    verification_status: VerificationStatus
    verification_submitted_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    
    user: Optional[UserPublicResponse] = None

    class Config:
        from_attributes = True

class CreatorCreateResponse(BaseModel):
    success: bool
    message: str
    creator_id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
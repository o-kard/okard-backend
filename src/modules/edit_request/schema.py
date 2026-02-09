from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.modules.common.enums import EditRequestStatus, VoteDecision
from src.modules.user.schema import UserPublicResponse

class EditRequestBase(BaseModel):
    post_id: UUID
    description: Optional[str] = None
    display_changes: Optional[str] = None
    proposed_changes: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class EditRequestCreate(EditRequestBase):
    pass

class EditRequestApproverOut(BaseModel):
    edit_request_id: UUID
    user_id: UUID
    rank: int
    contribution_amount: float

    class Config:
        from_attributes = True

class EditRequestOut(EditRequestBase):
    id: UUID
    requester_id: UUID
    status: EditRequestStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    proposed_changes: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    approvers: List[EditRequestApproverOut] = []

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    decision: VoteDecision
    comment: Optional[str] = None

class VoteCreate(VoteBase):
    pass

class VoteOut(VoteBase):
    edit_request_id: UUID
    user_id: UUID
    voted_at: datetime

    class Config:
        from_attributes = True

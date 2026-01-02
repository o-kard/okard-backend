import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Enum, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship # Added just in case, though not strictly in schema design yet
from src.database.db import Base
from src.modules.common.enums import EditRequestStatus, VoteDecision

class EditRequest(Base):
    __tablename__ = "edit_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), nullable=False)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    description = Column(String, nullable=True)
    display_changes = Column(String, nullable=True)
    proposed_changes = Column(JSONB, nullable=True)
    status = Column(Enum(EditRequestStatus), nullable=False, default=EditRequestStatus.pending)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    approvers = relationship("EditRequestApprover", backref="edit_request", cascade="all, delete-orphan")
    votes = relationship("EditRequestVote", backref="edit_request", cascade="all, delete-orphan")

class EditRequestApprover(Base):
    __tablename__ = "edit_request_approver"

    edit_request_id = Column(UUID(as_uuid=True), ForeignKey("edit_request.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    rank = Column(Integer, nullable=False)
    contribution_amount = Column(Integer, nullable=False)

class EditRequestVote(Base):
    __tablename__ = "edit_request_vote"

    edit_request_id = Column(UUID(as_uuid=True), ForeignKey("edit_request.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    decision = Column(Enum(VoteDecision), nullable=False)
    voted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    comment = Column(String, nullable=True)

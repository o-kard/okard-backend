from uuid import uuid4
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship, backref, query_expression, Mapped
from datetime import datetime
from src.database.db import Base
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional


class Comment(Base):
    __tablename__ = "comment"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comment.id", ondelete="CASCADE"), nullable=True)
    
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_liked: Mapped[bool] = query_expression()

    parent = relationship(
        "Comment",
        remote_side=[id],
        foreign_keys=[parent_id],
        backref=backref("children", cascade="all, delete-orphan", single_parent=True),
    )
    campaign = relationship("Campaign", back_populates="comments")
    author = relationship("User", back_populates="comments")

class CommentLike(Base):
    __tablename__ = "comment_like"

    comment_id = Column(UUID(as_uuid=True), ForeignKey("comment.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
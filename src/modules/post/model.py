import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Enum, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
import enum
from datetime import datetime, timezone

class PostState(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class PostStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class PostCategory(str, enum.Enum):
    tech = "tech"
    education = "education"
    health = "health"
    other = "other"

class Post(Base):
    __tablename__ = "post"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"),)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    effective_start_from = Column(DateTime, nullable=True)
    effective_end_date = Column(DateTime, nullable=True)
    state = Column(Enum(PostState), default=PostState.draft)
    status = Column(Enum(PostStatus), default=PostStatus.active)
    category = Column(Enum(PostCategory), default=PostCategory.other)
    goal_amount = Column(BigInteger, default=0)
    current_amount = Column(BigInteger, default=0)
    post_header = Column(String, nullable=False)
    post_description = Column(String, nullable=True)
    supporter = Column(Integer, default=0)

    user = relationship("User", back_populates="posts")
    images = relationship("Image", back_populates="post", cascade="all, delete", order_by="Image.order")
    campaigns = relationship("Campaign", back_populates="post", cascade="all, delete")
    rewards = relationship("Reward", back_populates="post", cascade="all, delete")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="post", cascade="all, delete")

    
    

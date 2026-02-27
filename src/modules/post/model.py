import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Enum, ForeignKey, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from datetime import datetime, timezone
from src.modules.common.enums import PostState, PostStatus, PostCategory



class PostEmbedding(Base):
    __tablename__ = "post_embedding"

    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), primary_key=True)
    embedding = Column(Text, nullable=True)

    post = relationship("Post", back_populates="embedding_data")


class Post(Base):
    __tablename__ = "post"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    effective_start_from = Column(DateTime(timezone=True), nullable=True)
    effective_end_date = Column(DateTime(timezone=True), nullable=True)
    state = Column(Enum(PostState), default=PostState.draft)
    status = Column(Enum(PostStatus), default=PostStatus.active)
    category = Column(Enum(PostCategory), default=PostCategory.art)
    goal_amount = Column(BigInteger, default=0)
    current_amount = Column(BigInteger, default=0)
    post_header = Column(String, nullable=False)
    post_description = Column(String, nullable=True)
    supporter = Column(Integer, default=0)
    
    user = relationship("User", back_populates="posts")
    campaigns = relationship("Campaign", back_populates="post", cascade="all, delete")
    rewards = relationship("Reward", back_populates="post", cascade="all, delete")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="post", cascade="all, delete")
    progress = relationship("Progress", back_populates="post", cascade="all, delete-orphan")
    
    embedding_data = relationship("PostEmbedding", uselist=False, back_populates="post", cascade="all, delete-orphan")
    contributors = relationship("Contributor", back_populates="post", cascade="all, delete-orphan")
    bookmarked_by = relationship("Bookmark", back_populates="post", cascade="all, delete-orphan")

    media = relationship(
        "Media",
        secondary="media_handler",
        primaryjoin="and_(Post.id==MediaHandler.reference_id, MediaHandler.type=='post')",
        secondaryjoin="MediaHandler.media_id==Media.id",
        order_by="Media.display_order",
        viewonly=True,
    )

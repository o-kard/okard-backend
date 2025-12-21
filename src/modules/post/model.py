import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Enum, ForeignKey, DateTime, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from datetime import datetime, timezone
from src.modules.common.enums import PostState, PostStatus, PostCategory

class PostState(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class PostStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class PostCategory(str, enum.Enum):
    art = "art"
    comics = "comics"
    crafts = "crafts"
    dance = "dance"
    design = "design"
    fashion = "fashion"
    filmVideo = "filmVideo"
    food = "food"
    games = "games"
    journalism = "journalism"
    music = "music"
    photography = "photography"
    publishing = "publishing"
    technology = "technology"
    theater = "theater"

class Post(Base):
    __tablename__ = "post"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
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

    images = relationship(
        "Image",
        secondary="imageHandler",
        primaryjoin="and_(Post.id==ImageHandler.reference_id, ImageHandler.type=='post')",
        secondaryjoin="ImageHandler.image_id==Image.id",
        order_by="Image.display_order",
        viewonly=True,
    )

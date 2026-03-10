from sqlalchemy import Column, String, Date, Integer, ForeignKey, and_, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from src.database.db import Base
from src.modules.common.enums import UserRole, UserStatus
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    clerk_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True, unique=True)
    # password removed as per schema request (Clerk auth)
    first_name = Column(String)
    middle_name = Column(String)
    surname = Column(String)
    address = Column(String)
    tel = Column(String)
    country_id = Column(UUID(as_uuid=True), ForeignKey("country.id"), nullable=True)
    birth_date = Column(Date)
    contribution_number = Column(Integer, default=0)
    role = Column(Enum(UserRole), default=UserRole.user)
    status = Column(Enum(UserStatus), default=UserStatus.active)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    posts = relationship("Post", back_populates="user")

    media = relationship(
        "Media",
        secondary="media_handler",
        primaryjoin="and_(User.id==MediaHandler.reference_id, MediaHandler.type=='user')",
        secondaryjoin="MediaHandler.media_id==Media.id",
        uselist=False,
        viewonly=True,
    )
    country = relationship("Country", back_populates="users")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    creator = relationship("Creator", back_populates="user", uselist=False, foreign_keys="Creator.user_id")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

    @property
    def campaign_number(self):
        return len(self.posts) if self.posts else 0

    @property
    def total_backers(self):
        if not self.posts:
            return 0
        return sum(post.supporter for post in self.posts if post.supporter)

    @property
    def user_description(self):
        return self.creator.bio if self.creator and hasattr(self.creator, "bio") else None
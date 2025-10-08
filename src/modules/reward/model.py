from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Reward(Base):
    __tablename__ = "reward"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    reward_header = Column(String, nullable=False)
    reward_description = Column(String, nullable=True)
    order = Column(Integer, default=0)
    reward_amount = Column(Integer,default=0)
    backup_amount = Column(Integer,default=0)

    post = relationship("Post", back_populates="rewards")  
    image = relationship("Image", back_populates="reward", cascade="all, delete")
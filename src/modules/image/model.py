import uuid
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Image(Base):
    __tablename__ = "image"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order = Column(Integer, nullable=False, default=1)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"), nullable=True)
    reward_id = Column(UUID(as_uuid=True), ForeignKey("reward.id"), nullable=True)
    orig_name = Column(String)
    media_type = Column(String)
    file_size = Column(BigInteger)
    path = Column(String)

    post = relationship("Post", back_populates="images")
    user = relationship("User", back_populates="image", uselist=False)
    campaign = relationship("Campaign", back_populates="image")
    reward = relationship("Reward", back_populates="image")

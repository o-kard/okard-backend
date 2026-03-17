from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Reward(Base):
    __tablename__ = "reward"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    reward_header = Column(String, nullable=False)
    reward_description = Column(String, nullable=True)
    display_order = Column(Integer, default=0)
    reward_amount = Column(Integer,default=0)
    backup_amount = Column(Integer,default=0)

    campaign = relationship("Campaign", back_populates="rewards")  

    media = relationship(
        "Media",
        secondary="media_handler",
        primaryjoin="and_(Reward.id==MediaHandler.reference_id, MediaHandler.type=='reward')",
        secondaryjoin="MediaHandler.media_id==Media.id",
        order_by="Media.display_order",
        viewonly=True,
    )
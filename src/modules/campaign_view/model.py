from sqlalchemy import Column, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.database.db import Base

class UserCampaignView(Base):
    __tablename__ = "user_campaign_view"

    # id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, primary_key=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"), nullable=False, primary_key=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

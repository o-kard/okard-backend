import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Enum, ForeignKey, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from datetime import datetime, timezone
from src.modules.common.enums import CampaignState, CampaignCategory



class CampaignEmbedding(Base):
    __tablename__ = "campaign_embedding"

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"), primary_key=True)
    embedding = Column(Text, nullable=True)

    campaign = relationship("Campaign", back_populates="embedding_data")


class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    effective_start_from = Column(DateTime(timezone=True), nullable=True)
    effective_end_date = Column(DateTime(timezone=True), nullable=True)
    state = Column(Enum(CampaignState), default=CampaignState.draft)
    category = Column(Enum(CampaignCategory), default=CampaignCategory.art)
    goal_amount = Column(BigInteger, default=0)
    current_amount = Column(BigInteger, default=0)
    post_header = Column(String, nullable=False)
    post_description = Column(String, nullable=True)
    supporter = Column(Integer, default=0)
    
    user = relationship("User", back_populates="campaigns")
    informations = relationship("Information", back_populates="campaign", cascade="all, delete")
    rewards = relationship("Reward", back_populates="campaign", cascade="all, delete")
    comments = relationship("Comment", back_populates="campaign", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="campaign", cascade="all, delete")
    progress = relationship("Progress", back_populates="campaign", cascade="all, delete-orphan")
    
    embedding_data = relationship("CampaignEmbedding", uselist=False, back_populates="campaign", cascade="all, delete-orphan")
    contributors = relationship("Contributor", back_populates="campaign", cascade="all, delete-orphan")
    bookmarked_by = relationship("Bookmark", back_populates="campaign", cascade="all, delete-orphan")

    media = relationship(
        "Media",
        secondary="media_handler",
        primaryjoin="and_(Campaign.id==MediaHandler.reference_id, MediaHandler.type=='campaign')",
        secondaryjoin="MediaHandler.media_id==Media.id",
        order_by="Media.display_order",
        viewonly=True,
    )

    @property
    def ai_label(self):
        if self.models:
            latest = sorted(self.models, key=lambda m: getattr(m, 'created_at', None) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)[0]
            return {
                "success_label": getattr(latest, "success_label", None),
                "risk_label": getattr(latest, "risk_label", None),
                "days_to_state_label": getattr(latest, "days_to_state_label", None),
                "goal_eval_label": getattr(latest, "goal_eval_label", None),
                "stretch_label": getattr(latest, "stretch_label", None)
            }
        return None

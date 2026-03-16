from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Information(Base):
    __tablename__ = "information"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    information_header = Column(String, nullable=False)
    information_description = Column(String, nullable=True)
    display_order = Column(Integer, default=0)

    campaign = relationship("Campaign", back_populates="informations")  

    media = relationship(
        "Media",
        secondary="media_handler",
        primaryjoin="and_(Information.id==MediaHandler.reference_id, MediaHandler.type=='information')",
        secondaryjoin="MediaHandler.media_id==Media.id",
        order_by="Media.display_order",
        viewonly=True,
    )

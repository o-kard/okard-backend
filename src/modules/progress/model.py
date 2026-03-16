from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    progress_header = Column(String, nullable=False)
    progress_description = Column(String, nullable=True)

    campaign = relationship("Campaign", back_populates="progress")

    media = relationship(
        "Media",
        secondary="media_handler",
        primaryjoin="and_(Progress.id==MediaHandler.reference_id, MediaHandler.type=='progress')",
        secondaryjoin="MediaHandler.media_id==Media.id",
        order_by="Media.display_order",
        viewonly=True,
    )

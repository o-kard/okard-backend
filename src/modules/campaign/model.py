from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    campaign_header = Column(String, nullable=False)
    campaign_description = Column(String, nullable=True)
    display_order = Column(Integer, default=0)

    post = relationship("Post", back_populates="campaigns")  

    images = relationship(
        "Image",
        secondary="imageHandler",
        primaryjoin="and_(Campaign.id==ImageHandler.reference_id, ImageHandler.type=='campaign')",
        secondaryjoin="ImageHandler.image_id==Image.id",
        order_by="Image.display_order",
        viewonly=True,
    )

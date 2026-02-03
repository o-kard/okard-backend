from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"),)
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

    post = relationship("Post", back_populates="progress")

    images = relationship(
        "Image",
        secondary="imageHandler",
        primaryjoin="and_(Progress.id==ImageHandler.reference_id, ImageHandler.type=='progress')",
        secondaryjoin="ImageHandler.image_id==Image.id",
        order_by="Image.display_order",
        viewonly=True,
    )

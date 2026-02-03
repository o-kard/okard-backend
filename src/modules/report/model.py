import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Enum, PrimaryKeyConstraint, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from src.modules.common.enums import ReportType, ReportStatus

class Report(Base):
    __tablename__ = "report"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), nullable=True)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    type = Column(Enum(ReportType), nullable=False)
    header = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.pending)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    files = relationship(
        "Image",
        secondary="imageHandler",
        primaryjoin="and_(Report.id==ImageHandler.reference_id, ImageHandler.type=='report')",
        secondaryjoin="ImageHandler.image_id==Image.id",
        order_by="Image.display_order",
        viewonly=True,
    )
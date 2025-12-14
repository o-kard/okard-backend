from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Enum, PrimaryKeyConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.database.db import Base
from src.modules.common.enums import ReportType

class Report(Base):
    __tablename__ = "report"

    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    type = Column(Enum(ReportType), primary_key=True)
    header = Column(String, nullable=True) # Request said header varchar
    description = Column(String, nullable=True) # Request said description varchar
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        PrimaryKeyConstraint('post_id', 'user_id', 'type'),
    )

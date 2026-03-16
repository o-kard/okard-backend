from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from src.modules.common.enums import NotificationType

class Notification(Base):
    __tablename__ = "notification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"), nullable=True)
    notification_title = Column(String, nullable=False)
    notification_message = Column(String, nullable=True)
    type = Column(Enum(NotificationType), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user  = relationship("User", foreign_keys=[user_id])   
    actor = relationship("User", foreign_keys=[actor_id])

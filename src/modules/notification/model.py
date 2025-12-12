from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import Column, DateTime, String, Integer, BigInteger, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class NotificationType(str, enum.Enum):
    comment = "comment"
    like = "like"
    system_alert = "system_alert"
    reminder = "reminder"
    goal = "goal"

# class NotificationStatus(str, enum.Enum):
#     unread = "unread"
#     read = "read"
#     dismissed = "dismissed"

class Notification(Base):
    __tablename__ = "notification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), nullable=True)
    notification_title = Column(String, nullable=False)
    notification_message = Column(String, nullable=True)
    type = Column(Enum(NotificationType), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


    user  = relationship("User", foreign_keys=[user_id])   
    actor = relationship("User", foreign_keys=[actor_id])

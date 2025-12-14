from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base

class Model(Base):
    __tablename__ = "model"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"))
    model_version = Column(String, nullable=True) 
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    success_label = Column(String, nullable=False)
    risk_label = Column(String, nullable=False)
    days_to_state_label = Column(String, nullable=False)
    category_label = Column(String, nullable=False)
    goal_eval_label = Column(String, nullable=False)
    stretch_label = Column(String, nullable=False)

    post = relationship("Post", back_populates="models")

from sqlalchemy import Column, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.database.db import Base

class UserPostView(Base):
    __tablename__ = "user_post_view"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

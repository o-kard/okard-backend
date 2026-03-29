from datetime import datetime, timezone
from sqlalchemy import Column, Enum, Integer, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.database.db import Base
from src.modules.common.enums import VerificationStatus

class Creator(Base):
    __tablename__ = "creators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    campaign_number = Column(Integer, default=0)
    social_links = Column(JSON, nullable=True)

    # Trust / Verification
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.pending)  # pending / verified / rejected
    verification_submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="creator", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])
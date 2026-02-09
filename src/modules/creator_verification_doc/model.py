from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from src.database.db import Base
from src.modules.common.enums import StorageProvider, VerificationDocType

class CreatorVerificationDoc(Base):
    __tablename__ = "creator_verification_doc"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creators.id"), nullable=False)
    type = Column(Enum(VerificationDocType), nullable=False)
    file_path = Column(String, nullable=False)
    storage_provider = Column(Enum(StorageProvider), nullable=False)
    mime_type = Column(String, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)

    creator = relationship("Creator", backref="verification_docs")
    verifier = relationship("User", foreign_keys=[verified_by])

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from src.modules.common.enums import PaymentMethod

class Payment(Base):
    __tablename__ = "payment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"),)
    amount = Column(Integer, default=0)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    payment_method = Column(Enum(PaymentMethod))

from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base


class PaymentMethod(str, enum.Enum):
    promtpay = "promptpay"
    card = "card"
    true_money_wallet = "true_money_wallet"
    pay_by_bank = "pay_by_bank"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"),)
    amount = Column(Integer, default=0)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"),)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    payment_method = Column(Enum(PaymentMethod))

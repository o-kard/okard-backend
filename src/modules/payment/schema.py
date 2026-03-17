from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from src.modules.common.enums import PaymentMethod

class PaymentBase(BaseModel):
    amount: int
    campaign_id: UUID
    full_name: str
    email: str
    payment_method: PaymentMethod

class PaymentCreate(PaymentBase):
    campaign_id: UUID

class PaymentUpdate(PaymentBase):
    campaign_id: Optional[UUID] = None             

class PaymentOut(PaymentBase):
    id: UUID
    created_at: datetime          
    class Config:
        from_attributes = True

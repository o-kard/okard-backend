from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from .model import PaymentMethod

class PaymentBase(BaseModel):
    amount: int
    post_id: UUID
    full_name: str
    email: str
    payment_method: PaymentMethod

class PaymentCreate(PaymentBase):
    post_id: UUID

class PaymentUpdate(PaymentBase):
    post_id: Optional[UUID] = None             

class PaymentOut(PaymentBase):
    id: UUID
    created_at: datetime          
    class Config:
        orm_mode = True

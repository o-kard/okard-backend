# src/modules/payment/service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from . import repo, schema, model
from src.modules.contributor import service as contributor_service
from src.modules.post import repo as post_repo

def list_payments(db: Session) -> List[model.Payment]:
    return repo.list_payments(db)

def get_payment(db: Session, payment_id: UUID) -> model.Payment:
    db_payment = repo.get_payment(db, payment_id)
    if not db_payment:
        raise ValueError("Payment not found")
    return db_payment

def create_payment(db: Session, clerk_id: str, data: schema.PaymentCreate) -> model.Payment:
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    payload = schema.PaymentCreate(**data.model_dump(), user_id=user.id)

    db_payment = repo.create_payment(db, payload)

    contributor_service.ensure_and_add_amount(
        db=db,
        user_id=user.id,
        post_id=payload.post_id,
        amount=payload.amount,
    )

    post_repo.increment_current_amount(
        db=db,
        post_id=payload.post_id,
        delta=payload.amount
    )

    return db_payment

def delete_payment(db: Session, payment_id: UUID) -> model.Payment:
    db_payment = get_payment(db, payment_id)
    return repo.delete_payment(db, db_payment)

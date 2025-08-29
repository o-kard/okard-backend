# src/modules/payment/repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from . import model, schema

def list_payments(db: Session):
    return db.query(model.Payment).all()

def get_payment(db: Session, payment_id: UUID):
    return db.query(model.Payment).filter(model.Payment.id == payment_id).first()

def create_payment(db: Session, payment: schema.PaymentCreate):
    db_payment = model.Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def delete_payment(db: Session, db_payment: model.Payment):
    db.delete(db_payment)
    db.commit()
    return db_payment

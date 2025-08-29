from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import service, schema
from src.database.db import get_db 

router = APIRouter(prefix="/payment", tags=["payment"])

@router.get("", response_model=List[schema.PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return service.list_payments(db)

@router.get("/{payment_id}", response_model=schema.PaymentOut)
def get_payment(payment_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.get_payment(db, payment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("", response_model=schema.PaymentOut, status_code=201)
def create_payment(payload: schema.PaymentCreate, clerk_id: str = Query(...), db: Session = Depends(get_db)):
    return service.create_payment(db,clerk_id, payload)

@router.delete("/{payment_id}")
def delete_payment(payment_id: UUID, db: Session = Depends(get_db)):
    try:
        service.delete_payment(db, payment_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

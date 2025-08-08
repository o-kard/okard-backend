# controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from . import schema, service
from uuid import UUID


router = APIRouter(prefix="/tests", tags=["Test"])

@router.get("/", response_model=list[schema.TestOut])
def list_tests(db: Session = Depends(get_db)):
    return service.list_tests(db)

@router.get("/{test_id}", response_model=schema.TestOut)
def get_test(test_id: UUID, db: Session = Depends(get_db)):
    test = service.get_test(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.post("/", response_model=schema.TestOut)
def create_test(test: schema.TestCreate, db: Session = Depends(get_db)):
    return service.add_test(db, test)

@router.put("/{test_id}", response_model=schema.TestOut)
def update_test(test_id: UUID, test: schema.TestUpdate, db: Session = Depends(get_db)):
    updated = service.update_test(db, test_id, test)
    if not updated:
        raise HTTPException(status_code=404, detail="Test not found")
    return updated

@router.delete("/{test_id}", response_model=schema.TestOut)
def delete_test(test_id: UUID, db: Session = Depends(get_db)):
    deleted = service.delete_test(db, test_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return deleted

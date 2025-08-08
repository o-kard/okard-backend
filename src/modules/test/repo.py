# repo.py
from sqlalchemy.orm import Session
from . import model, schema

def list_tests(db: Session):
    return db.query(model.Test).all()

def get_test(db: Session, test_id: int):
    return db.query(model.Test).filter(model.Test.id == test_id).first()

def add_test(db: Session, test: schema.TestCreate):
    db_test = model.Test(**test.model_dump())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def update_test(db: Session, test_id: int, test: schema.TestUpdate):
    db_test = get_test(db, test_id)
    if not db_test:
        return None
    for key, value in test.model_dump().items():
        setattr(db_test, key, value)
    db.commit()
    db.refresh(db_test)
    return db_test

def delete_test(db: Session, test_id: int):
    db_test = get_test(db, test_id)
    if not db_test:
        return None
    db.delete(db_test)
    db.commit()
    return db_test

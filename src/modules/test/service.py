# service.py
from sqlalchemy.orm import Session
from . import schema, repo

def list_tests(db: Session):
    return repo.list_tests(db)

def get_test(db: Session, test_id: int):
    return repo.get_test(db, test_id)

def add_test(db: Session, test: schema.TestCreate):
    return repo.add_test(db, test)

def update_test(db: Session, test_id: int, test: schema.TestUpdate):
    return repo.update_test(db, test_id, test)

def delete_test(db: Session, test_id: int):
    return repo.delete_test(db, test_id)

# modules/user/service.py
from sqlalchemy.orm import Session
from . import repo, schema

def create_user_from_clerk(db: Session, user_data: schema.UserCreate):
    return repo.create_user(db, user_data)

def get_user_by_clerk_id(db: Session, clerk_id: str):
    return repo.get_user_by_clerk_id(db, clerk_id)


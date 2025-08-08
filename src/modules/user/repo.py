# modules/user/repo.py
from sqlalchemy.orm import Session
from . import model, schema

def get_user_by_clerk_id(db: Session, clerk_id: str):
    return db.query(model.User).filter(model.User.clerk_id == clerk_id).first()

def create_user(db: Session, user: schema.UserCreate):
    existing_user = get_user_by_clerk_id(db, user.clerk_id)
    if existing_user:
        raise ValueError("User with this Clerk ID already exists.")
    db_user = model.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


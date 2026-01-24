# modules/user/repo.py
from sqlalchemy.orm import Session
from . import model, schema

def get_user_by_clerk_id(db: Session, clerk_id: str):
    return db.query(model.User).filter(model.User.clerk_id == clerk_id).first()

async def create_user(db: Session, user_data: schema.UserCreate):
    existing_user = get_user_by_clerk_id(db, user_data.clerk_id)
    if existing_user:
        raise ValueError("User with this Clerk ID already exists.")
    db_user = model.User(**user_data.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id, user_data: schema.UserUpdate):
    existing_user = get_user_by_clerk_id(db, user_data.clerk_id)
    if (not existing_user) or (existing_user.id != user_id):
        raise ValueError("User Invalid.")
    # ใช้ exclude_unset เพื่ออัปเดตเฉพาะฟิลด์ที่ส่งมา
    data = user_data.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(existing_user, k, v)
    db.commit()
    db.refresh(existing_user)
    return existing_user

def list_users(db: Session):
    return db.query(model.User).all()
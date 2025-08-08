# modules/user/controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schema, service
from src.database.db import get_db


router = APIRouter(prefix="/user", tags=["user"])

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/", response_model=schema.UserOut)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    return service.create_user_from_clerk(db, user)

@router.get("/me", response_model=schema.UserOut)
def get_user_by_clerk_id(clerk_id: str, db: Session = Depends(get_db)):
    user = service.get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

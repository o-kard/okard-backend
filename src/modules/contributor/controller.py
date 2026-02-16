from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.db import get_db
from . import service, schema
from typing import List

router = APIRouter(prefix="/contributor", tags=["Contributor"])

@router.get("/{user_id}", response_model=List[schema.ContributorWithPostOut])
def get_contribute_by_user_id(user_id: UUID, db: Session = Depends(get_db)):
    return service.get_contributions_by_user(db, user_id)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.database.db import get_db
from . import service, schema
from src.modules.auth import get_current_user

router = APIRouter(prefix="/creator-verification-doc", tags=["Creator Verification Doc"])

@router.get("/creator/{creator_id}", response_model=List[schema.CreatorVerificationDocOut])
async def get_verification_docs(
    creator_id: UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):
    # TODO: Add permission check if needed (only creator themselves or admin)
    return service.get_verification_docs(db, creator_id)

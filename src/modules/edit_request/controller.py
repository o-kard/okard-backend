from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.database.db import get_db
from . import schema, service, repo
from src.modules.user.service import get_user_by_clerk_id

router = APIRouter(prefix="/edit_requests", tags=["Edit Requests"])

@router.post("/", response_model=schema.EditRequestOut)
async def create_edit_request(
    data: schema.EditRequestCreate,
    clerk_id: str,
    db: Session = Depends(get_db)
):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.create_request(db, user.id, data)

@router.get("/{request_id}", response_model=schema.EditRequestOut)
def get_edit_request(request_id: UUID, db: Session = Depends(get_db)):
    req = repo.get_edit_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


@router.get("/", response_model=list[schema.EditRequestOut])
def list_pending_requests(campaign_id: UUID, db: Session = Depends(get_db)):
    return service.get_pending_requests(db, campaign_id)

@router.post("/{request_id}/vote", response_model=schema.VoteOut)
async def cast_vote(
    request_id: UUID,
    data: schema.VoteCreate,
    clerk_id: str,
    db: Session = Depends(get_db)
):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await service.cast_vote(db, request_id, user.id, data)

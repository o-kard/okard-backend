import json
from uuid import UUID
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.params import Query
from sqlalchemy.orm import Session
from typing import List
from src.database.db import get_db
from . import service, schema

router = APIRouter(prefix="/comment", tags=["Comment"])

@router.post("", response_model=schema.CommentOut)
async def add_comment(
    data: str = Form(...), 
    db: Session = Depends(get_db),
    clerk_id: str = Query(...),
):
    try:
        comment_obj = schema.CommentCreate(**json.loads(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    return await service.add_comment(db, comment_obj, clerk_id)

@router.get("/post/{post_id}", response_model=List[schema.CommentOut])
async def list_comments(post_id: UUID, clerk_id: str | None = Query(None), db: Session = Depends(get_db)):
    return await service.list_comments(db, post_id, clerk_id)

@router.put("/{comment_id}/like")
async def like_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    clerk_id: str = Query(...),
):
    try:
        return await service.like(db, comment_id, clerk_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Comment not found")

@router.delete("/{comment_id}/like")
async def unlike_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),  
    clerk_id: str = Query(...),
):
    print(comment_id, clerk_id)
    try:
        return await service.unlike(db, comment_id, clerk_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Comment not found")

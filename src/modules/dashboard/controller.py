from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from . import service, schema

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/users/{user_id}/summary", response_model=schema.UserDashboardSummary)
def user_summary(user_id: UUID, db: Session = Depends(get_db)):
    return service.get_user_dashboard(db, user_id)

@router.get("/users/{user_id}/posts", response_model=list[schema.PostProgress])
def user_posts_progress(
    user_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return service.get_post_progress(db, user_id, limit, offset)

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from . import service, schema

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=schema.UserDashboardSummary)
def user_summary(clerk_id: str = Query(...), db: Session = Depends(get_db)):
    return service.get_user_dashboard(db, clerk_id)

@router.get("/posts", response_model=list[schema.PostProgress])
def user_posts_progress(
    clerk_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return service.get_post_progress(db, clerk_id, limit, offset)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.database.db import get_db
from . import service as recommend_service
from . import schema as recommend_schema

router = APIRouter(
    prefix="/post",
    tags=["Post Recommendation"]
)

@router.get(
    "/{post_id}/recommend",
    response_model=recommend_schema.PostRecommendResponse
)
def recommend_post(
    post_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    try:
        recs = recommend_service.recommend_by_post(
            db,
            post_id=post_id,
            top_k=limit
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "source_post_id": post_id,
        "recommendations": recs
    }

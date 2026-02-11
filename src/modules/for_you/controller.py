from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.modules.auth import get_optional_current_user
from src.modules.for_you.schema import ForYouResponse
from src.modules.for_you.service import for_you
from src.modules.user.repo import get_user_by_clerk_id

router = APIRouter(prefix="/post", tags=["Post"])

@router.get(
    "/for-you",
    response_model=ForYouResponse
)
def for_you_endpoint(
    db: Session = Depends(get_db),
    payload: dict | None = Depends(get_optional_current_user),
    limit: int = Query(10, ge=1, le=50),
    
): 
    user_id = None
    if payload:
        clerk_id = payload["sub"]
        user = get_user_by_clerk_id(db, clerk_id)
        if user:
            user_id = user.id

    campaigns = for_you(
        db,
        user_id=user_id,
        limit=limit
    )

    return {
        "user_id": user_id, # Can be None
        "campaigns": campaigns
    }


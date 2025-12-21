from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.modules.user.repo import get_user_by_clerk_id
from src.modules.for_you.service import for_you
from src.modules.for_you.schema import ForYouResponse

router = APIRouter(
    prefix="/post",
    tags=["For You"]
)

@router.get(
    "/for-you",
    response_model=ForYouResponse
)
def for_you_endpoint(
    db: Session = Depends(get_db),
    clerk_id: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    
):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    campaigns = for_you(
        db,
        user_id=user.id,
        limit=limit
    )

    return {
        "user_id": user.id,
        "campaigns": campaigns
    }


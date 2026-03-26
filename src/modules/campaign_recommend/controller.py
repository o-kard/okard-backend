from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.database.db import get_db
from . import service as recommend_service
from . import schema as recommend_schema

router = APIRouter(
    prefix="/campaign_recommend",
    tags=["Campaign Recommendation"]
)

from src.modules.auth import get_optional_current_user

@router.get(
    "/{campaign_id}/recommend",
    response_model=recommend_schema.CampaignRecommendResponse
)
async def recommend_campaign(
    campaign_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_optional_current_user),
):
    clerk_id = payload.get("sub") if payload else None
    try:
        recs = await recommend_service.recommend_by_campaign(
            db,
            campaign_id=campaign_id,
            top_k=limit,
            clerk_id=clerk_id
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {
        "source_campaign_id": campaign_id,
        "recommendations": recs
    }

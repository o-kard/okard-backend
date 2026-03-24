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

@router.get(
    "/{campaign_id}/recommend",
    response_model=recommend_schema.CampaignRecommendResponse
)
def recommend_campaign(
    campaign_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    try:
        recs = recommend_service.recommend_by_campaign(
            db,
            campaign_id=campaign_id,
            top_k=limit
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {
        "source_campaign_id": campaign_id,
        "recommendations": recs
    }

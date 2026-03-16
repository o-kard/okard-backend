# src/modules/home/controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from src.database.db import get_db
from .service import get_top_pledged_campaigns

from .schema import CategoryStat
from .service import get_category_stats_service

from .schema import HomeCampaignOut

router = APIRouter(prefix="/home", tags=["home"])


@router.get(
    "/top-pledged-campaigns",
    response_model=list[HomeCampaignOut],
)
def get_top_pledged_campaigns_controller(
    limit: int = 10,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_top_pledged_campaigns(
        db=db,
        limit=limit,
        category=category,
    )
    
@router.get(
    "/category-stats",
    response_model=list[CategoryStat],
)
def get_category_stats(
    db: Session = Depends(get_db),
):
    return get_category_stats_service(db)
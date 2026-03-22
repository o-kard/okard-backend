# src/modules/home/controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from src.database.db import get_db
from src.modules.auth import get_optional_current_user
from .service import get_top_pledged_campaigns_service

from .schema import CategoryStat
from .service import get_category_stats_service

from .schema import HomeCampaignOut
from fastapi import Query

router = APIRouter(prefix="/home", tags=["home"])

@router.get(
    "/top-pledged-campaigns",
    response_model=list[HomeCampaignOut],
)
async def get_top_pledged_campaigns_controller(
    limit: int = 10,
    category: Optional[str] = None,
    payload: Optional[dict] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    return await get_top_pledged_campaigns_service(
        db=db,
        limit=limit,
        category=category,
        payload=payload,
    )
    
@router.get(
    "/category-stats",
    response_model=list[CategoryStat],
)
def get_category_stats(
    db: Session = Depends(get_db),
):
    return get_category_stats_service(db)
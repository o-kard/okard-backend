from .repo import get_top_pledged_campaigns
from .repo import get_category_stats
from .schema import CategoryStat
from sqlalchemy.orm import Session
from src.modules.user.service import get_user_by_clerk_id
from uuid import UUID

async def get_top_pledged_campaigns_service(
    db: Session,
    limit: int = 10,
    category: str | None = None,
    payload: dict | None = None,
):
    user_id = None
    if payload:
        clerk_id = payload.get("sub")
        user = await get_user_by_clerk_id(db, clerk_id)
        if user:
            user_id = user.id

    campaigns = get_top_pledged_campaigns(
        db=db,
        limit=limit,
        category=category,
        user_id=user_id,
    )

    return campaigns

def get_category_stats_service(db: Session) -> list[CategoryStat]:
    rows = get_category_stats(db)

    return [
        CategoryStat(
            category=row.category,
            total_projects=row.total_projects,
            funded_projects=row.funded_projects,
            total_raised=row.total_raised,
        )
        for row in rows
    ]
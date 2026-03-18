# src/modules/home/repo.py
from sqlalchemy.orm import Session, selectinload
from src.modules.campaign.model import Campaign
from sqlalchemy import func, case

def get_top_pledged_campaigns(
    db: Session,
    limit: int,
    category: str | None = None,
):
    query = (
        db.query(Campaign)
        .options(
            selectinload(Campaign.media),
            selectinload(Campaign.user),
        )
    )

    if category:
        query = query.filter(Campaign.category == category)

    return (
        query
        .order_by(Campaign.current_amount.desc())
        .limit(limit)
        .all()
    )
    
def get_category_stats(db: Session):
    funded_case = case(
        (Campaign.current_amount >= Campaign.goal_amount, 1),
        else_=0,
    )

    return (
        db.query(
            Campaign.category.label("category"),
            func.count(Campaign.id).label("total_projects"),
            func.sum(funded_case).label("funded_projects"),
            func.coalesce(func.sum(Campaign.current_amount), 0).label("total_raised"),
        )
        .group_by(Campaign.category)
        .all()
    )
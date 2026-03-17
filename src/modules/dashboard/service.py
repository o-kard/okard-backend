from datetime import date
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.modules.common.enums import UserRole
from src.modules.user.service import get_user_by_clerk_id
from . import repo, schema

async def validate_creator(db: Session, clerk_id: str):
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != UserRole.creator:
        raise HTTPException(status_code=403, detail="Permission denied. Creators only.")
    return user

async def get_user_dashboard(db: Session, clerk_id: str) -> schema.UserDashboardSummary:
    user = await validate_creator(db, clerk_id)
    campaign_count, unique_investors, total_raised, hit_goal_count = repo.get_user_summary(db, user.id)
    return schema.UserDashboardSummary(
        user_id=user.id,
        campaign_count=campaign_count,
        unique_investor_count=unique_investors,
        total_raised=int(total_raised),
        hit_goal_campaign_count=hit_goal_count,
    )

async def get_campaign_progress(db: Session, clerk_id: str, limit: int = 20, offset: int = 0) -> list[schema.CampaignProgress]:
    user = await validate_creator(db, clerk_id)
    rows = repo.list_campaign_progress(db, user.id, limit, offset)
    out: list[schema.CampaignProgress] = []
    for (campaign_id, title, goal_amount, current_amount, investor_count) in rows:
        goal = int(goal_amount or 0)
        cur = int(current_amount or 0)
        progress = 0.0 if goal == 0 else round(cur * 100.0 / goal, 2)
        out.append(schema.CampaignProgress(
            campaign_id=campaign_id,
            title=title,
            goal_amount=goal,
            current_amount=cur,
            progress_pct=progress,
            investor_count=int(investor_count or 0),
            hit_goal=cur >= goal,
        ))
    return out

async def get_payment_stats(db: Session, clerk_id: str):
    user = await validate_creator(db, clerk_id)
    return repo.list_payment_stats(db, user.id)

async def get_investor_country_stats(db: Session, clerk_id: str):
    user = await validate_creator(db, clerk_id)
    return repo.list_investor_countries(db, user.id)

async def list_trending_campaigns(db, day: date, clerk_id: str):
    user = await validate_creator(db, clerk_id)
    return repo.get_trending_campaigns(db, day, user.id)
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from . import repo, schema

def get_user_dashboard(db: Session, clerk_id: str) -> schema.UserDashboardSummary:
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post_count, unique_investors, total_raised, hit_goal_count = repo.get_user_summary(db, user.id)
    return schema.UserDashboardSummary(
        user_id=user.id,
        post_count=post_count,
        unique_investor_count=unique_investors,
        total_raised=int(total_raised),
        hit_goal_post_count=hit_goal_count,
    )

def get_post_progress(db: Session, clerk_id: str, limit: int = 20, offset: int = 0) -> list[schema.PostProgress]:
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    rows = repo.list_post_progress(db, user.id, limit, offset)
    out: list[schema.PostProgress] = []
    for (post_id, title, goal_amount, current_amount, investor_count) in rows:
        goal = int(goal_amount or 0)
        cur = int(current_amount or 0)
        progress = 0.0 if goal == 0 else round(cur * 100.0 / goal, 2)
        out.append(schema.PostProgress(
            post_id=post_id,
            title=title,
            goal_amount=goal,
            current_amount=cur,
            progress_pct=progress,
            investor_count=int(investor_count or 0),
            hit_goal=cur >= goal,
        ))
    return out

def get_payment_stats(db: Session, clerk_id: str):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.list_payment_stats(db, user.id)

def get_investor_country_stats(db: Session, clerk_id: str):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.list_investor_countries(db, user.id)

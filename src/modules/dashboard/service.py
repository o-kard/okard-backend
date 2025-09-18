from uuid import UUID
from sqlalchemy.orm import Session
from . import repo, schema

def get_user_dashboard(db: Session, user_id: UUID) -> schema.UserDashboardSummary:
    post_count, unique_investors, total_raised, hit_goal_count = repo.get_user_summary(db, user_id)
    return schema.UserDashboardSummary(
        user_id=user_id,
        post_count=post_count,
        unique_investor_count=unique_investors,
        total_raised=int(total_raised),
        hit_goal_post_count=hit_goal_count,
    )

def get_post_progress(db: Session, user_id: UUID, limit: int = 20, offset: int = 0) -> list[schema.PostProgress]:
    rows = repo.list_post_progress(db, user_id, limit, offset)
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

from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session

from src.modules.post import model as post_model
from src.modules.contributor import model as contr_model

def get_user_summary(db: Session, user_id: UUID):
    q_post_count = select(func.count(post_model.Post.id)).where(
        post_model.Post.user_id == user_id
    )
    post_count = db.scalar(q_post_count) or 0

    q_total_raised = (
        select(func.coalesce(func.sum(contr_model.Contributor.total_amount), 0))
        .join_from(contr_model.Contributor, post_model.Post,
                   contr_model.Contributor.post_id == post_model.Post.id)
        .where(post_model.Post.user_id == user_id)                                                                                                      
    )
    total_raised = db.scalar(q_total_raised) or 0

    q_unique_investors = (
        select(func.count(distinct(contr_model.Contributor.user_id)))
        .join_from(contr_model.Contributor, post_model.Post,
                   contr_model.Contributor.post_id == post_model.Post.id)
        .where(post_model.Post.user_id == user_id)
    )
    unique_investors = db.scalar(q_unique_investors) or 0

    q_hit_goal = select(func.count(post_model.Post.id)).where(
        post_model.Post.user_id == user_id,
        post_model.Post.current_amount >= post_model.Post.goal_amount,
    )
    hit_goal_count = db.scalar(q_hit_goal) or 0

    return post_count, unique_investors, total_raised, hit_goal_count


def list_post_progress(db: Session, user_id: UUID, limit: int = 20, offset: int = 0):
    investor_count_expr = func.coalesce(
        func.count(distinct(contr_model.Contributor.user_id)), 0
    ).label("investor_count")

    stmt = (
        select(
            post_model.Post.id,
            post_model.Post.post_header,
            post_model.Post.goal_amount,
            post_model.Post.current_amount,
            investor_count_expr,
        )
        .join(
            contr_model.Contributor,
            contr_model.Contributor.post_id == post_model.Post.id,
            isouter=True,
        )
        .where(post_model.Post.user_id == user_id)
        .group_by(post_model.Post.id)
        .order_by(post_model.Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).all()

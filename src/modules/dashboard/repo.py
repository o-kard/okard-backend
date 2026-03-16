from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Date, cast, desc, select, func, distinct
from sqlalchemy.orm import Session

from src.modules.campaign import model as campaign_model
from src.modules.contributor import model as contributor_model
from src.modules.country import model as country_model
from src.modules.user import model as user_model
from src.modules.payment import model as payment_model

def get_user_summary(db: Session, user_id: UUID):
    q_campaign_count = select(func.count(campaign_model.Campaign.id)).where(
        campaign_model.Campaign.user_id == user_id
    )
    campaign_count = db.scalar(q_campaign_count) or 0

    q_total_raised = (
        select(func.coalesce(func.sum(contributor_model.Contributor.total_amount), 0))
        .join_from(contributor_model.Contributor, campaign_model.Campaign,
                   contributor_model.Contributor.campaign_id == campaign_model.Campaign.id)
        .where(campaign_model.Campaign.user_id == user_id)                                                                                                      
    )
    total_raised = db.scalar(q_total_raised) or 0

    q_unique_investors = (
        select(func.count(distinct(contributor_model.Contributor.user_id)))
        .join_from(contributor_model.Contributor, campaign_model.Campaign,
                   contributor_model.Contributor.campaign_id == campaign_model.Campaign.id)
        .where(campaign_model.Campaign.user_id == user_id)
    )
    unique_investors = db.scalar(q_unique_investors) or 0

    q_hit_goal = select(func.count(campaign_model.Campaign.id)).where(
        campaign_model.Campaign.user_id == user_id,
        campaign_model.Campaign.current_amount >= campaign_model.Campaign.goal_amount,
    )
    hit_goal_count = db.scalar(q_hit_goal) or 0

    return campaign_count, unique_investors, total_raised, hit_goal_count


def list_campaign_progress(db: Session, user_id: UUID, limit: int = 20, offset: int = 0):
    investor_count_expr = func.coalesce(
        func.count(distinct(contributor_model.Contributor.user_id)), 0
    ).label("investor_count")

    stmt = (
        select(
            campaign_model.Campaign.id,
            campaign_model.Campaign.campaign_header,
            campaign_model.Campaign.goal_amount,
            campaign_model.Campaign.current_amount,
            investor_count_expr,
        )
        .join(
            contributor_model.Contributor,
            contributor_model.Contributor.campaign_id == campaign_model.Campaign.id,
            isouter=True,
        )
        .where(campaign_model.Campaign.user_id == user_id)
        .group_by(campaign_model.Campaign.id)
        .order_by(campaign_model.Campaign.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).all()

def list_payment_stats(db: Session, user_id: UUID):
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    stmt = (
        select(
            cast(func.date(payment_model.Payment.created_at), Date).label("date"),
            func.sum(payment_model.Payment.amount).label("total_amount"),
        )
        .join(campaign_model.Campaign, payment_model.Payment.campaign_id == campaign_model.Campaign.id)
        .where(
            campaign_model.Campaign.user_id == user_id,
            payment_model.Payment.created_at >= seven_days_ago
        )
        .group_by(cast(func.date(payment_model.Payment.created_at), Date))
        .order_by("date")
    )
    return db.execute(stmt).all()

def list_investor_countries(db: Session, user_id: UUID):
    stmt = (
        select(
            country_model.Country.name.label("country"),
            func.count(func.distinct(contributor_model.Contributor.user_id)).label("invest_count"),
        )
        .join(campaign_model.Campaign, campaign_model.Campaign.id == contributor_model.Contributor.campaign_id)
        .join(user_model.User, user_model.User.id == contributor_model.Contributor.user_id)
        .join(country_model.Country, country_model.Country.id == user_model.User.country_id)
        .where(campaign_model.Campaign.user_id == user_id)
        .group_by(country_model.Country.name)
    )
    return db.execute(stmt).all()

def get_trending_campaigns(db: Session, day: date, user_id: UUID,limit: int = 5):
    return (
        db.query(
            campaign_model.Campaign.id.label("campaign_id"),
            campaign_model.Campaign.campaign_header,
            func.count(payment_model.Payment.id).label("donate_count")
        )
        .join(payment_model.Payment, payment_model.Payment.campaign_id == campaign_model.Campaign.id)
        .filter(campaign_model.Campaign.user_id == user_id)
        .filter(cast(payment_model.Payment.created_at, Date) == day)
        .group_by(campaign_model.Campaign.id)
        .order_by(desc("donate_count"))
        .limit(limit)
        .all()
    )

from sqlalchemy.orm import Session, joinedload
from . import model, schema
from uuid import UUID
from src.modules.information import model as info_model
from src.modules.media import model as media_model
from src.modules.reward import model as reward_model
from src.modules.user import model as user_model
from typing import Optional

from .model import Campaign
from src.modules.bookmark.repo import hydrate_campaign_bookmarks
from sqlalchemy import or_, desc, asc, select, exists
from datetime import datetime, timezone
from src.modules.bookmark.model import Bookmark
from src.modules.common.enums import CampaignState
from src.modules.contributor.model import Contributor
from src.modules.user.model import User
from src.modules.country.model import Country
from sqlalchemy import func


def list_campaigns(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    state: str | None = "published",
    owner_id: UUID | None = None,
    current_user_id: UUID | None = None,
    limit: int | None = None,
    offset: int | None = None,
    include_closed: bool = True
):
    query = db.query(model.Campaign).options(
        joinedload(Campaign.user).joinedload(user_model.User.media),
        joinedload(Campaign.user).joinedload(user_model.User.campaigns),
        joinedload(Campaign.user).joinedload(user_model.User.creator),
        joinedload(model.Campaign.media),
        joinedload(model.Campaign.informations).joinedload(info_model.Information.media), 
        joinedload(model.Campaign.rewards).joinedload(reward_model.Reward.media),
        joinedload(model.Campaign.models),
    )

    if owner_id:
        query = query.filter(model.Campaign.user_id == owner_id)

    if state and state not in ["all", "admin_all"]:
        query = query.filter(model.Campaign.state == state)
    elif state == "all" and not owner_id:
        query = query.filter(model.Campaign.state != CampaignState.draft, model.Campaign.state != CampaignState.suspend)

    if category:
        query = query.filter(model.Campaign.category == category)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                model.Campaign.campaign_header.ilike(search),
                model.Campaign.campaign_description.ilike(search)
            )
        )

    if not include_closed:
        now = datetime.now(timezone.utc)
        query = query.filter(model.Campaign.effective_end_date > now)

    if sort == "newest":
        query = query.order_by(desc(model.Campaign.created_at))
    elif sort == "ending_soon":
        now = datetime.now(timezone.utc)
        query = query.filter(model.Campaign.effective_end_date > now).order_by(asc(model.Campaign.effective_end_date))
    elif sort == "popular":
        query = query.order_by(desc(model.Campaign.supporter))
    elif sort == "updated":
         query = query.order_by(desc(model.Campaign.updated_at))
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    campaigns = query.all()
    
    hydrate_campaign_bookmarks(db, campaigns, current_user_id)

    return campaigns

def list_campaigns_paginated(
    db: Session,
    category: Optional[str] = None,
    q: Optional[str] = None,
    sort: Optional[str] = "newest",
    state: Optional[str] = "published",
    current_user_id: UUID | None = None,
    owner_id: UUID | None = None,
    limit: int | None = None,
    offset: int | None = None,
    include_closed: bool = True
):
    query = db.query(model.Campaign).options(
        joinedload(Campaign.user).joinedload(user_model.User.media),
        joinedload(Campaign.user).joinedload(user_model.User.campaigns),
        joinedload(Campaign.user).joinedload(user_model.User.creator),
        joinedload(model.Campaign.media),
        joinedload(model.Campaign.informations).joinedload(info_model.Information.media), 
        joinedload(model.Campaign.rewards).joinedload(reward_model.Reward.media),
        joinedload(model.Campaign.models),
    )

    if owner_id:
        query = query.filter(model.Campaign.user_id == owner_id)

    if state and state not in ["all", "admin_all"]:
        query = query.filter(model.Campaign.state == state)
    elif state == "all" and not owner_id:
        query = query.filter(model.Campaign.state != CampaignState.draft, model.Campaign.state != CampaignState.suspend)

    if category:
        query = query.filter(model.Campaign.category == category)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                model.Campaign.campaign_header.ilike(search),
                model.Campaign.campaign_description.ilike(search)
            )
        )

    if not include_closed:
        now = datetime.now(timezone.utc)
        query = query.filter(model.Campaign.effective_end_date > now)

    # Calculate total before pagination
    total = query.count()

    if sort == "newest":
        query = query.order_by(desc(model.Campaign.created_at))
    elif sort == "ending_soon":
        now = datetime.now(timezone.utc)
        query = query.filter(model.Campaign.effective_end_date > now).order_by(asc(model.Campaign.effective_end_date))
    elif sort == "popular":
        query = query.order_by(desc(model.Campaign.supporter))
    elif sort == "updated":
        query = query.order_by(desc(model.Campaign.updated_at))
        
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    campaigns = query.all()
    
    hydrate_campaign_bookmarks(db, campaigns, current_user_id)

    return campaigns, total

def get_campaign(db: Session, campaign_id, user_id: UUID | None = None):
    campaign = (
        db.query(model.Campaign)
        .options( 
            joinedload(Campaign.user).joinedload(user_model.User.media),
            joinedload(Campaign.user).joinedload(user_model.User.campaigns),
            joinedload(Campaign.user).joinedload(user_model.User.creator),
            joinedload(model.Campaign.media),
            joinedload(model.Campaign.informations).joinedload(info_model.Information.media),
            joinedload(model.Campaign.rewards).joinedload(reward_model.Reward.media),
            joinedload(model.Campaign.models),
        )
        .filter(model.Campaign.id == campaign_id)
        .first()
    )
    
    if campaign and user_id:
        hydrate_campaign_bookmarks(db, [campaign], user_id)
        
    return campaign

def update_campaign(db: Session, db_campaign: model.Campaign, data: schema.CampaignUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_campaign, key, value)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

# Repo to update campaign state
def update_campaign_state(db: Session, db_campaign: model.Campaign, state: schema.CampaignState):
    db_campaign.state = state
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, db_campaign: model.Campaign):
    db.delete(db_campaign)
    db.commit()
    return db_campaign

def create_campaign_by_user(db: Session, user_id: UUID, data: schema.CampaignCreate) -> model.Campaign:
    db_campaign = model.Campaign(**data.model_dump(), user_id=user_id)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def increment_current_amount(db: Session, campaign_id: UUID, delta: int):
    db.query(model.Campaign).filter(model.Campaign.id == campaign_id).update(
        {model.Campaign.current_amount: model.Campaign.current_amount + delta},
        synchronize_session=False
    )
    db.commit()

def increment_supporter(db: Session, campaign_id: UUID):
    db.query(model.Campaign).filter(model.Campaign.id == campaign_id).update(
        {model.Campaign.supporter: model.Campaign.supporter + 1},
        synchronize_session=False
    )
    db.commit()

def update_campaign_prediction(db: Session, campaign_id: UUID, result: dict):
    db.query(Campaign).filter(Campaign.id == campaign_id).update({
        Campaign.success_label: result.get("success_cls", {}).get("label"),
        Campaign.risk_label: result.get("risk_level", {}).get("label"),
        Campaign.goal_eval_label: result.get("goal_eval", {}).get("label"),
        Campaign.category_label: result.get("recommend_category", {}).get("label"),
        Campaign.days_to_state_label: result.get("days_to_state_change", {}).get("label"),
        Campaign.stretch_label: result.get("stretch_potential_cls", {}).get("label"),
    })


def get_campaign_community_stats(db: Session, campaign_id: UUID):
    # Get total supporters
    total_supporters = db.query(func.count(func.distinct(Contributor.user_id))).filter(
        Contributor.campaign_id == campaign_id
    ).scalar() or 0

    # Get top 10 countries by supporter count
    query = (
        db.query(Country.en_name, func.count(func.distinct(Contributor.user_id)))
        .join(User, User.country_id == Country.id)
        .join(Contributor, Contributor.user_id == User.id)
        .filter(Contributor.campaign_id == campaign_id)
        .group_by(Country.en_name)
        .order_by(func.count(func.distinct(Contributor.user_id)).desc())
        .limit(10)
    )
    results = query.all()
    
    top_countries = [
        {"country": name, "supporter": count}
        for name, count in results
    ]

    return {
        "total_supporters": total_supporters,
        "top_countries": top_countries
    }

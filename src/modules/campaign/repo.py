from sqlalchemy.orm import Session, joinedload
from . import model, schema
from uuid import UUID
from src.modules.information import model as info_model
from src.modules.media import model as media_model
from src.modules.reward import model as reward_model
from src.modules.user import model as user_model

from .model import Campaign

from sqlalchemy import or_, desc, asc, select, exists
from datetime import datetime, timezone
from src.modules.bookmark.model import Bookmark
from src.modules.common.enums import CampaignState
from src.modules.contributor.model import Contributor
from src.modules.user.model import User
from sqlalchemy import func


def list_campaigns(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    state: str | None = "published",
    owner_id: UUID | None = None,
    current_user_id: UUID | None = None
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

    if state and state != "all":
        query = query.filter(model.Campaign.state == state)
    elif state == "all" and not owner_id:
        query = query.filter(model.Campaign.state != CampaignState.draft, model.Campaign.state != CampaignState.suspend)

    if category:
        query = query.filter(model.Campaign.category == category)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                model.Campaign.post_header.ilike(search),
                model.Campaign.post_description.ilike(search)
            )
        )

    if sort == "newest":
        query = query.order_by(desc(model.Campaign.created_at))
    elif sort == "ending_soon":
        now = datetime.now(timezone.utc)
        query = query.filter(model.Campaign.effective_end_date > now).order_by(asc(model.Campaign.effective_end_date))
    elif sort == "popular":
        query = query.order_by(desc(model.Campaign.supporter))
    elif sort == "updated":
         query = query.order_by(desc(model.Campaign.updated_at))
    else:
        query = query.order_by(desc(model.Campaign.created_at))

    campaigns = query.all()
    
    # Optional: Attach is_bookmarked if current_user_id is provided
    if current_user_id and campaigns:
        campaign_ids = [p.id for p in campaigns]
        bookmarked_ids = db.execute(
            select(Bookmark.campaign_id)
            .where(Bookmark.user_id == current_user_id, Bookmark.campaign_id.in_(campaign_ids))
        ).scalars().all()
        bookmarked_set = set(bookmarked_ids)
        for p in campaigns:
            p.is_bookmarked = p.id in bookmarked_set

    return campaigns

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
        is_bookmarked = db.execute(
            select(exists().where(Bookmark.user_id == user_id, Bookmark.campaign_id == campaign_id))
        ).scalar()
        campaign.is_bookmarked = is_bookmarked
        
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

    # Get contributors and their addresses
    contributors = db.query(User.address).join(
        Contributor, Contributor.user_id == User.id
    ).filter(
        Contributor.campaign_id == campaign_id
    ).all()

    # Simple logic to group by a generalized "city" from address
    city_counts = {}
    for (address,) in contributors:
        if not address:
            continue
        # Mock logic: assume address contains province names, or simply use the whole address if short
        # We can extract common Thai province names or just take the last part of a comma-separated address
        parts = [p.strip() for p in address.split(",") if p.strip()]
        city = parts[-1] if parts else "Unknown"
        
        # Fallback to some known cities if address is messy (for demo purposes)
        city_counts[city] = city_counts.get(city, 0) + 1

    # Format the result and get top cities
    top_cities = [
        {"city": city, "supporter": count}
        for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    return {
        "total_supporters": total_supporters,
        "top_cities": top_cities
    }

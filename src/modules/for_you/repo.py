from sqlalchemy.orm import Session
from src.modules.campaign.model import Campaign, CampaignEmbedding
from src.modules.campaign_view.model import UserCampaignView
from sqlalchemy.sql.expression import func
from src.modules.common.enums import CampaignState

def get_recent_viewed_campaign_embeddings(
    db: Session,
    user_id,
    limit: int,
):
    return (
        db.query(Campaign.id, CampaignEmbedding.embedding)
        .join(UserCampaignView, UserCampaignView.campaign_id == Campaign.id)
        .join(CampaignEmbedding, Campaign.embedding_data)
        .filter(
            UserCampaignView.user_id == user_id,
            CampaignEmbedding.embedding.isnot(None),
            Campaign.user_id != user_id,
            Campaign.state == CampaignState.published,
        )
        .order_by(UserCampaignView.viewed_at.desc())
        .limit(limit)
        .all()
    )


def get_seen_campaign_ids(db: Session, user_id):
    return {
        pid for (pid,) in
        db.query(UserCampaignView.campaign_id)
        .filter(UserCampaignView.user_id == user_id)
        .all()
    }


def get_candidate_campaign_embeddings(db: Session, user_id):
    return (
        db.query(Campaign.id, CampaignEmbedding.embedding)
        .join(CampaignEmbedding, Campaign.embedding_data)
        .filter(
            CampaignEmbedding.embedding.isnot(None),
            Campaign.user_id != user_id,
            Campaign.state == CampaignState.published,
        )
        .all()
    )

def get_fallback_popular_campaign_ids(db: Session, limit: int):
    return [
        pid for (pid,) in
        db.query(Campaign.id)
        .join(CampaignEmbedding, Campaign.embedding_data)
        .filter(
            CampaignEmbedding.embedding.isnot(None),
            Campaign.state == CampaignState.published,
        )
        .order_by(func.random())
        .limit(limit)
        .all()
    ]
    
def get_campaigns_by_ids(db: Session, campaign_ids: list[str]):
    if not campaign_ids:
        return []

    ordering = {str(pid): i for i, pid in enumerate(campaign_ids)}

    campaigns = (
        db.query(Campaign)
        .filter(Campaign.id.in_(campaign_ids))
        .all()
    )

    campaigns.sort(key=lambda p: ordering.get(str(p.id), 9999))
    return campaigns

def get_user_category_affinity(db: Session, user_id):
    rows = (
        db.query(Campaign.category)
        .join(UserCampaignView, UserCampaignView.campaign_id == Campaign.id)
        .filter(UserCampaignView.user_id == user_id)
        .all()
    )

    freq = {}
    for (cat,) in rows:
        freq[cat] = freq.get(cat, 0) + 1

    total = sum(freq.values()) or 1
    return {k: v / total for k, v in freq.items()}



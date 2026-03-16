from sqlalchemy.orm import Session
from src.modules.campaign.model import Campaign, CampaignEmbedding
from src.modules.common.enums import CampaignState
from uuid import UUID

def get_campaign_by_id(db: Session, campaign_id: UUID) -> Campaign | None:
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()

def list_candidates(db: Session, source: Campaign):
    # แนะนำเฉพาะแคมเปญที่ active + published (คุณปรับได้)
    return (
        db.query(Campaign)
        .join(CampaignEmbedding, Campaign.embedding_data)
        .filter(
            Campaign.id != source.id,
            CampaignEmbedding.embedding.isnot(None),
            Campaign.state == CampaignState.published
        )
        .all()
    )

def fallback_same_category(db: Session, source: Campaign, limit: int):
    return (
        db.query(Campaign)
        .filter(
            Campaign.id != source.id,
            Campaign.category == source.category
        )
        .limit(limit)
        .all()
    )

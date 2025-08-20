from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_campaigns(db: Session):
    return db.query(model.Campaign).all()

def get_campaign(db: Session, campaign_id: UUID):
    return db.query(model.Campaign).filter(model.Campaign.id == campaign_id).first()

def create_campaign(db: Session, campaign: schema.CampaignCreate):
    db_campaign = model.Campaign(**campaign.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def update_campaign(db: Session, db_campaign: model.Campaign, data: schema.CampaignUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_campaign, key, value)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, db_campaign: model.Campaign):
    db.delete(db_campaign)
    db.commit()
    return db_campaign

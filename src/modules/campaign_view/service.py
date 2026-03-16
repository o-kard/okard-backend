from sqlalchemy.orm import Session
from .repo import upsert_view

def log_campaign_view(db: Session, user_id, campaign_id):
    upsert_view(db, user_id, campaign_id)
    db.commit()

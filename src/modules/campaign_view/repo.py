from sqlalchemy.sql import func
from .model import UserCampaignView

def upsert_view(db, user_id, campaign_id):
    view = db.query(UserCampaignView).filter(
        UserCampaignView.user_id == user_id,
        UserCampaignView.campaign_id == campaign_id
    ).first()

    if view:
        view.viewed_at = func.now()
    else:
        new_view = UserCampaignView(
            user_id=user_id,
            campaign_id=campaign_id,
        )
        db.add(new_view)

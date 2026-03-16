from sqlalchemy.orm import Session
from src.modules.user.model import User
from src.modules.campaign.model import Campaign

class SearchRepository:

    @staticmethod
    def search_users(db: Session, query: str):
        return (
            db.query(User)
            .filter(
                (User.username.ilike(f"%{query}%")) |
                (User.first_name.ilike(f"%{query}%")) |
                (User.surname.ilike(f"%{query}%"))
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_campaigns(db: Session, query: str):
        return (
            db.query(Campaign)
            .filter(
                (Campaign.campaign_header.ilike(f"%{query}%")) |
                (Campaign.campaign_description.ilike(f"%{query}%"))
            )
            .limit(10)
            .all()
        )

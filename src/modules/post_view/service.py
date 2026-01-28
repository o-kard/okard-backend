from sqlalchemy.orm import Session
from .repo import upsert_view

def log_post_view(db: Session, user_id, post_id):
    upsert_view(db, user_id, post_id)
    db.commit()

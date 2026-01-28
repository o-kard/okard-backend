from sqlalchemy.sql import func
from .model import UserPostView

def upsert_view(db, user_id, post_id):
    view = db.query(UserPostView).filter(
        UserPostView.user_id == user_id,
        UserPostView.post_id == post_id
    ).first()

    if view:
        view.viewed_at = func.now()
    else:
        new_view = UserPostView(
            user_id=user_id,
            post_id=post_id,
        )
        db.add(new_view)

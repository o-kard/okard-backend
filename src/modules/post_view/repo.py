from .model import UserPostView

def insert_view(db, user_id, post_id):
    view = UserPostView(
        user_id=user_id,
        post_id=post_id,
    )
    db.add(view)

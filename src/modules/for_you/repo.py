from sqlalchemy.orm import Session
from src.modules.post.model import Post
from src.modules.post_view.model import UserPostView

def get_recent_viewed_post_embeddings(
    db: Session,
    user_id,
    limit: int,
):
    return (
        db.query(Post.id, Post.embedding)
        .join(UserPostView, UserPostView.post_id == Post.id)
        .filter(
            UserPostView.user_id == user_id,
            Post.embedding.isnot(None),
            Post.user_id != user_id,
        )
        .order_by(UserPostView.viewed_at.desc())
        .limit(limit)
        .all()
    )


def get_seen_post_ids(db: Session, user_id):
    return {
        pid for (pid,) in
        db.query(UserPostView.post_id)
        .filter(UserPostView.user_id == user_id)
        .all()
    }


def get_candidate_post_embeddings(db: Session, user_id):
    return (
        db.query(Post.id, Post.embedding)
        .filter(
            Post.embedding.isnot(None),
            Post.user_id != user_id,
        )
        .all()
    )


def get_fallback_popular_post_ids(db: Session, limit: int):
    return [
        pid for (pid,) in
        db.query(Post.id)
        .filter(Post.embedding.isnot(None))
        .order_by(Post.supporter.desc(), Post.created_at.desc())
        .limit(limit)
        .all()
    ]
    
def get_posts_by_ids(db: Session, post_ids: list[str]):
    if not post_ids:
        return []

    ordering = {pid: i for i, pid in enumerate(post_ids)}

    posts = (
        db.query(Post)
        .filter(Post.id.in_(post_ids))
        .all()
    )

    posts.sort(key=lambda p: ordering.get(str(p.id), 9999))
    return posts

def get_user_category_affinity(db: Session, user_id):
    rows = (
        db.query(Post.category)
        .join(UserPostView, UserPostView.post_id == Post.id)
        .filter(UserPostView.user_id == user_id)
        .all()
    )

    freq = {}
    for (cat,) in rows:
        freq[cat] = freq.get(cat, 0) + 1

    total = sum(freq.values()) or 1
    return {k: v / total for k, v in freq.items()}



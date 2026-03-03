from sqlalchemy.orm import Session
from src.modules.post.model import Post, PostEmbedding
from src.modules.common.enums import PostState
from uuid import UUID

def get_post_by_id(db: Session, post_id: UUID) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()

def list_candidates(db: Session, source: Post):
    # แนะนำเฉพาะโพสต์ที่ active + published (คุณปรับได้)
    return (
        db.query(Post)
        .join(PostEmbedding, Post.embedding_data)
        .filter(
            Post.id != source.id,
            PostEmbedding.embedding.isnot(None),
            Post.state == PostState.published
        )
        .all()
    )

def fallback_same_category(db: Session, source: Post, limit: int):
    return (
        db.query(Post)
        .filter(
            Post.id != source.id,
            Post.category == source.category
        )
        .limit(limit)
        .all()
    )

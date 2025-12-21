from sqlalchemy.orm import Session
from src.modules.post.model import Post
from uuid import UUID

def get_post_by_id(db: Session, post_id: UUID) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()

def list_candidates(db: Session, source: Post):
    # แนะนำเฉพาะโพสต์ที่ active + published (คุณปรับได้)
    return (
        db.query(Post)
        .filter(
            Post.id != source.id,
            Post.embedding.isnot(None),
            Post.status == source.status,   # หรือใช้ PostStatus.active ตรงๆก็ได้
            Post.state == source.state      # หรือเลือก published เท่านั้น
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

# src/modules/home/repo.py
from sqlalchemy.orm import Session, selectinload
from src.modules.post.model import Post
from sqlalchemy import func, case

def get_top_pledged_posts(
    db: Session,
    limit: int,
    category: str | None = None,
):
    query = (
        db.query(Post)
        .options(
            selectinload(Post.media),
            selectinload(Post.user),
        )
    )

    if category:
        query = query.filter(Post.category == category)

    return (
        query
        .order_by(Post.current_amount.desc())
        .limit(limit)
        .all()
    )
    
def get_category_stats(db: Session):
    funded_case = case(
        (Post.current_amount >= Post.goal_amount, 1),
        else_=0,
    )

    return (
        db.query(
            Post.category.label("category"),
            func.count(Post.id).label("total_projects"),
            func.sum(funded_case).label("funded_projects"),
            func.coalesce(func.sum(Post.current_amount), 0).label("total_raised"),
        )
        .group_by(Post.category)
        .all()
    )
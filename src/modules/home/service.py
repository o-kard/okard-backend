from .repo import get_top_pledged_posts
from .repo import get_category_stats
from .schema import CategoryStat
from sqlalchemy.orm import Session
# from .mapper import map_post_to_home

def get_top_pledged_campaigns(
    db,
    limit: int = 10,
    category: str | None = None,
):
    posts = get_top_pledged_posts(
        db=db,
        limit=limit,
        category=category,
    )

    return posts

def get_category_stats_service(db: Session) -> list[CategoryStat]:
    rows = get_category_stats(db)

    return [
        CategoryStat(
            category=row.category,
            total_projects=row.total_projects,
            funded_projects=row.funded_projects,
            total_raised=row.total_raised,
        )
        for row in rows
    ]
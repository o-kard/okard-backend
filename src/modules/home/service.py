# src/modules/home/service.py
from .schema import HomeCampaign, HomeImage, HomeCreator
from .repo import get_top_pledged_posts
from .repo import get_category_stats
from .schema import CategoryStat
from sqlalchemy.orm import Session

def map_post_to_home(p) -> HomeCampaign:
    progress = (
        int((p.current_amount / p.goal_amount) * 100)
        if p.goal_amount else 0
    )

    return HomeCampaign(
        id=str(p.id),
        user_id=str(p.user_id),
        category=p.category,

        post_header=p.post_header,
        post_description=p.post_description,

        goal_amount=p.goal_amount,
        current_amount=p.current_amount,
        progress=progress,
        supporter=p.supporter,

        images=[
            HomeImage(path=img.path)
            for img in (p.images or [])
        ],

        creator=HomeCreator(
            id=str(p.user.id),
            name=p.user.username,
            avatar=p.user.image.path,
        ),
    )


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

    return [map_post_to_home(p) for p in posts]

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
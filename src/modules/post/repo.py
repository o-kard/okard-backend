from sqlalchemy.orm import Session, joinedload
from . import model, schema
from uuid import UUID
from src.modules.campaign import model as camp_model
from src.modules.image import model as image_model
from src.modules.reward import model as reward_model
from src.modules.user import model as user_model

from .model import Post

from sqlalchemy import or_, desc, asc
from datetime import datetime, timezone

def list_posts(
    db: Session,
    category: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    state: str | None = "published",
    status: str | None = "active"
):
    query = db.query(model.Post).options(
        joinedload(Post.user).load_only(user_model.User.username).joinedload(user_model.User.image),
        joinedload(model.Post.images),
        joinedload(model.Post.campaigns).joinedload(camp_model.Campaign.images), 
        joinedload(model.Post.rewards).joinedload(reward_model.Reward.images),
    )

    if status and status != "all":
        query = query.filter(model.Post.status == status)

    if state and state != "all":
        query = query.filter(model.Post.state == state)

    if category:
        query = query.filter(model.Post.category == category)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                model.Post.post_header.ilike(search),
                model.Post.post_description.ilike(search)
            )
        )

    if sort == "newest":
        query = query.order_by(desc(model.Post.created_at))
    elif sort == "ending_soon":
        now = datetime.now(timezone.utc)
        query = query.filter(model.Post.effective_end_date > now).order_by(asc(model.Post.effective_end_date))
    elif sort == "popular":
        query = query.order_by(desc(model.Post.supporter))
    elif sort == "updated":
         query = query.order_by(desc(model.Post.created_at))
    else:
        query = query.order_by(desc(model.Post.created_at))

    return query.all()

def get_post(db: Session, post_id):
    return (
        db.query(model.Post)
        .options( 
            joinedload(Post.user).load_only(user_model.User.username).joinedload(user_model.User.image),
            joinedload(model.Post.images),
            joinedload(model.Post.campaigns).joinedload(camp_model.Campaign.images),
            joinedload(model.Post.rewards).joinedload(reward_model.Reward.images),
        )
        .filter(model.Post.id == post_id)
        .first()
    )

def update_post(db: Session, db_post: model.Post, data: schema.PostUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

# Repo to update post status
def update_post_status(db: Session, db_post: model.Post, status: schema.PostStatus):
    db_post.status = status
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, db_post: model.Post):
    db.delete(db_post)
    db.commit()
    return db_post

def create_post_by_user(db: Session, user_id: UUID, data: schema.PostCreate) -> model.Post:
    db_post = model.Post(**data.model_dump(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def increment_current_amount(db: Session, post_id: UUID, delta: int):
    db.query(model.Post).filter(model.Post.id == post_id).update(
        {model.Post.current_amount: model.Post.current_amount + delta},
        synchronize_session=False
    )
    db.commit()

def increment_supporter(db: Session, post_id: UUID):
    db.query(model.Post).filter(model.Post.id == post_id).update(
        {model.Post.supporter: model.Post.supporter + 1},
        synchronize_session=False
    )
    db.commit()

def update_post_prediction(db: Session, post_id: UUID, result: dict):
    db.query(Post).filter(Post.id == post_id).update({
        Post.success_label: result.get("success_cls", {}).get("label"),
        Post.risk_label: result.get("risk_level", {}).get("label"),
        Post.goal_eval_label: result.get("goal_eval", {}).get("label"),
        Post.category_label: result.get("recommend_category", {}).get("label"),
        Post.days_to_state_label: result.get("days_to_state_change", {}).get("label"),
        Post.stretch_label: result.get("stretch_potential_cls", {}).get("label"),
    })


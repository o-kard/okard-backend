from sqlalchemy.orm import Session, joinedload
from . import model, schema
from uuid import UUID
from src.modules.campaign import model as camp_model
from src.modules.image import model as image_model
from src.modules.reward import model as reward_model

def list_posts(db: Session):
    return (
        db.query(model.Post)
        .options(
            joinedload(model.Post.images),
            joinedload(model.Post.campaigns).joinedload(camp_model.Campaign.image), 
            joinedload(model.Post.rewards).joinedload(reward_model.Reward.image),
        ).all()
    )

def get_post(db: Session, post_id):
    return (
        db.query(model.Post)
        .options(
            joinedload(model.Post.images),
            joinedload(model.Post.campaigns).joinedload(camp_model.Campaign.image),
            joinedload(model.Post.rewards).joinedload(reward_model.Reward.image),
        )
        .filter(model.Post.id == post_id)
        .first()
    )

def update_post(db: Session, db_post: model.Post, data: schema.PostUpdate):
    for key, value in data.model_dump().items():
        setattr(db_post, key, value)
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

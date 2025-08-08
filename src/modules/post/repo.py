from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_posts(db: Session):
    return db.query(model.Post).all()

def get_post(db: Session, post_id: UUID):
    return db.query(model.Post).filter(model.Post.id == post_id).first()

def create_post(db: Session, post: schema.PostCreate):
    db_post = model.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

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

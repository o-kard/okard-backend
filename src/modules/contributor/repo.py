# src/modules/contributor/repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from . import model

def get_by_user_and_post(db: Session, user_id: UUID, post_id: UUID):
    return db.query(model.Contributor).filter(
        model.Contributor.user_id == user_id,
        model.Contributor.post_id == post_id
    ).first()

def create(db: Session, user_id: UUID, post_id: UUID, amount: int):
    c = model.Contributor(user_id=user_id, post_id=post_id, total_amount=amount)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

def add_amount(db: Session, contributor: model.Contributor, amount: int):
    contributor.total_amount += amount
    db.commit()
    db.refresh(contributor)
    return contributor

def list_contributors(db: Session):
    return db.query(model.Contributor).all()

def delete_contributor(db: Session, contributor_id: UUID):
    c = db.query(model.Contributor).filter(model.Contributor.id == contributor_id).first()
    if c:
        db.delete(c)
        db.commit()
    return c

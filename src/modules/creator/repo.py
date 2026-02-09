from sqlalchemy.orm import Session, joinedload
import uuid
from datetime import datetime, timezone

from .model import Creator
from .schema import CreatorCreate, CreatorUpdate

def create_creator(db: Session, creator_data: CreatorCreate, user_id: uuid.UUID) -> Creator:
    creator = Creator(
        user_id=user_id,
        bio=creator_data.bio,
        social_links=creator_data.social_links,
        verification_submitted_at=datetime.now(timezone.utc)
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator

def get_creator_by_id(db: Session, creator_id: uuid.UUID) -> Creator:
    return (
        db.query(Creator)
        .options(joinedload(Creator.user))
        .filter(Creator.id == creator_id)
        .first()
    )

def get_creator_by_user_id(db: Session, user_id: uuid.UUID) -> Creator:
    return (
        db.query(Creator)
        .options(joinedload(Creator.user))
        .filter(Creator.user_id == user_id)
        .first()
    )

def update_creator(db: Session, creator_id: uuid.UUID, creator_data: CreatorUpdate) -> Creator:
    creator = get_creator_by_id(db, creator_id)
    if not creator:
        return None
    
    # Update only provided fields
    update_data = creator_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(creator, field, value)
    
    db.commit()
    db.refresh(creator)
    return creator

def list_creators(db: Session):
    return db.query(Creator).all()

def delete_creator(db: Session, creator_id: uuid.UUID):
    creator = get_creator_by_id(db, creator_id)
    if creator:
        db.delete(creator)
        db.commit()
    return creator

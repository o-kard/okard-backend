# src/modules/contributor/service.py
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, model

def list_contributors(db: Session):
    return repo.list_contributors(db)

def get_contributor(db: Session, user_id: UUID, post_id: UUID) -> model.Contributor | None:
    return repo.get_by_user_and_post(db, user_id, post_id)

def ensure_and_add_amount(db: Session, user_id: UUID, post_id: UUID, amount: int) -> model.Contributor:
    c = repo.get_by_user_and_post(db, user_id, post_id)
    if c:
        return repo.add_amount(db, c, amount)
    return repo.create(db, user_id, post_id, amount)

def delete_contributor(db: Session, contributor_id: UUID):
    return repo.delete_contributor(db, contributor_id)

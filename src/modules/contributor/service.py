# src/modules/contributor/service.py
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, model

def list_contributors(db: Session):
    return repo.list_contributors(db)

def get_contributor(db: Session, user_id: UUID, post_id: UUID) -> model.Contributor | None:
    return repo.get_by_user_and_post(db, user_id, post_id)

def ensure_and_add_amount(db: Session, user_id: UUID, post_id: UUID, amount: int) -> tuple[model.Contributor, bool]:
    c = repo.get_by_user_and_post(db, user_id, post_id)
    if c:
        return repo.add_amount(db, c, amount), False
    return repo.create(db, user_id, post_id, amount), True

def delete_contributor(db: Session, contributor_id: UUID):
    return repo.delete_contributor(db, contributor_id)

def get_contributions_by_user(db: Session, user_id: UUID):
    return repo.get_by_user_id(db, user_id)

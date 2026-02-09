from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from .model import CreatorVerificationDoc
from . import schema

def create_verification_doc(db: Session, doc: schema.CreatorVerificationDocCreate) -> CreatorVerificationDoc:
    db_doc = CreatorVerificationDoc(**doc.model_dump())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_verification_doc(db: Session, doc_id: UUID) -> Optional[CreatorVerificationDoc]:
    return db.query(CreatorVerificationDoc).filter(CreatorVerificationDoc.id == doc_id).first()

def get_verification_docs_by_creator(db: Session, creator_id: UUID) -> List[CreatorVerificationDoc]:
    return db.query(CreatorVerificationDoc).filter(CreatorVerificationDoc.creator_id == creator_id).all()

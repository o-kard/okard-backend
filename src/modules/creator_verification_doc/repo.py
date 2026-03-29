from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
import os
from pathlib import Path
from datetime import datetime, timezone
from .model import CreatorVerificationDoc
from . import schema
from src.modules.common.enums import StorageProvider
from src.modules.common.minio_service import MinioService

BASE_DIR = Path(__file__).resolve().parents[3]
minio_service = MinioService()

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

def verify_all_docs(db: Session, creator_id: UUID, admin_id: UUID):
    docs = get_verification_docs_by_creator(db, creator_id)
    now = datetime.now(timezone.utc)
    for doc in docs:
        doc.verified_at = now
        doc.verified_by = admin_id
    db.commit()

def delete_all_docs(db: Session, creator_id: UUID):
    docs = get_verification_docs_by_creator(db, creator_id)
    for doc in docs:
        if doc.storage_provider == StorageProvider.minio:
            if doc.file_path:
                minio_service.delete_file(doc.file_path)
        elif doc.storage_provider == StorageProvider.local:
            if doc.file_path:
                local_path = BASE_DIR / doc.file_path
                if local_path.exists():
                    os.remove(local_path)
        db.delete(doc)
    db.commit()

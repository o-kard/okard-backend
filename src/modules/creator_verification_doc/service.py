from sqlalchemy.orm import Session
from fastapi import UploadFile
from uuid import UUID, uuid4
import os
from pathlib import Path
from typing import Optional

from src.modules.common.enums import StorageProvider, VerificationDocType
from . import repo, schema

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads" / "verification_docs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def create_verification_doc_from_upload(
    db: Session,
    creator_id: UUID,
    doc_type: VerificationDocType,
    file: UploadFile
) -> schema.CreatorVerificationDocOut:
    
    content = await file.read()
    ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as f:
        f.write(content)

    doc_create = schema.CreatorVerificationDocCreate(
        creator_id=creator_id,
        type=doc_type,
        file_path=str(file_path.relative_to(BASE_DIR)), # Store relative path
        storage_provider=StorageProvider.minio,
        mime_type=file.content_type,
        file_size=len(content)
    )

    return repo.create_verification_doc(db, doc_create)

def get_verification_docs(db: Session, creator_id: UUID):
    return repo.get_verification_docs_by_creator(db, creator_id)

from sqlalchemy.orm import Session
from fastapi import UploadFile
from uuid import UUID, uuid4
import os
from pathlib import Path
from typing import Optional

from src.modules.common.enums import StorageProvider, VerificationDocType
from . import repo, schema
from src.modules.common.minio_service import MinioService

minio_service = MinioService()

async def create_verification_doc_from_upload(
    db: Session,
    creator_id: UUID,
    doc_type: VerificationDocType,
    file: UploadFile
) -> schema.CreatorVerificationDocOut:
    
    # Store file content for size checking
    content = await file.read()
    await file.seek(0)
    
    # Upload to MinIO
    folder_path = f"verification_docs/{creator_id}"
    minio_url = minio_service.upload_file(file, folder=folder_path)
    
    if not minio_url:
        raise ValueError("Failed to upload file to MinIO")

    doc_create = schema.CreatorVerificationDocCreate(
        creator_id=creator_id,
        type=doc_type,
        file_path=minio_url,
        storage_provider=StorageProvider.minio,
        mime_type=file.content_type,
        file_size=len(content)
    )

    return repo.create_verification_doc(db, doc_create)

def get_verification_docs(db: Session, creator_id: UUID):
    return repo.get_verification_docs_by_creator(db, creator_id)

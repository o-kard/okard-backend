from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile
from . import repo, schema, model
from src.modules.image import service as image_service

async def create_report(db: Session, reporter_id: UUID, data: schema.ReportCreate, files: Optional[List[UploadFile]] = None):
    report = repo.create_report(db, reporter_id, data)
    
    if files:
        await image_service._save_files_and_create_images(
            db=db,
            parent_type="report",
            parent_id=report.id,
            files=files
        )
        
    return report

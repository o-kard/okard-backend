from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from . import repo, schema, model
from src.modules.media import service as media_service
from src.modules.common.enums import ReportStatus
from src.modules.common.file_utils import validate_file

async def create_report(db: Session, reporter_id: UUID, data: schema.ReportCreate, files: Optional[List[UploadFile]] = None):
    if files:
        for file in files:
            validate_file(file)

    try:
        report = repo.create_report(db, reporter_id, data)
        
        if files:
            await media_service._save_files_and_create_media(
                db=db,
                parent_type="report",
                parent_id=report.id,
                files=files,
                commit=False
            )
        
        db.commit()
        db.refresh(report)
        return report

    except Exception as e:
        db.rollback()
        raise e

def list_reports(db: Session):
    return repo.get_reports(db)

def update_report_status(db: Session, report_id: UUID, status: ReportStatus):
    report = repo.update_report_status(db, report_id, status)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

def delete_report(db: Session, report_id: UUID):
    success = repo.delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}

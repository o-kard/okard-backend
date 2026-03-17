from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.database.db import get_db
from . import schema, service
from src.modules.user.service import get_user_by_clerk_id
from src.modules.common.enums import ReportType, ReportStatus

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=schema.ReportOut)
async def create_report(
    campaign_id: Optional[UUID] = Form(None),
    type: ReportType = Form(...),
    header: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    clerk_id: str = Query(...),
    db: Session = Depends(get_db)
):
    data = schema.ReportCreate(
        campaign_id=campaign_id,
        type=type,
        header=header,
        description=description
    )
    
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return await service.create_report(db, user.id, data, files)

@router.get("", response_model=List[schema.ReportOut])
def list_reports(db: Session = Depends(get_db)):
    return service.list_reports(db)

@router.put("/{report_id}/status", response_model=schema.ReportOut)
def update_report_status(
    report_id: UUID,
    status: str = Query(...), 
    db: Session = Depends(get_db)
):
    try:
        enum_status = ReportStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    return service.update_report_status(db, report_id, enum_status)

@router.delete("/{report_id}")
def delete_report(report_id: UUID, db: Session = Depends(get_db)):
    return service.delete_report(db, report_id)

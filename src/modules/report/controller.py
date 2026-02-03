from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.database.db import get_db
from . import schema, service
from src.modules.user.service import get_user_by_clerk_id
from src.modules.common.enums import ReportType

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=schema.ReportOut)
async def create_report(
    post_id: Optional[UUID] = Form(None),
    type: ReportType = Form(...),
    header: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    clerk_id: str = Query(...),
    db: Session = Depends(get_db)
):
    data = schema.ReportCreate(
        post_id=post_id,
        type=type,
        header=header,
        description=description
    )
    
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return await service.create_report(db, user.id, data, files)

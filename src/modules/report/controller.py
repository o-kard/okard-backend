from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from . import schema, service
from src.modules.user.service import get_user_by_clerk_id

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=schema.ReportOut)
def create_report(
    data: schema.ReportCreate,
    clerk_id: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.create_report(db, user.id, data)

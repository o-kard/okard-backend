from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model

def create_report(db: Session, reporter_id: UUID, data: schema.ReportCreate):
    return repo.create_report(db, reporter_id, data)

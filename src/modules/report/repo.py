from sqlalchemy.orm import Session
from uuid import UUID
from . import model, schema

def create_report(db: Session, reporter_id: UUID, data: schema.ReportCreate) -> model.Report:
    db_obj = model.Report(
        post_id=data.post_id,
        reporter_id=reporter_id,
        type=data.type,
        header=data.header,
        description=data.description
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_report(db: Session, report_id: UUID) -> model.Report:
    return db.query(model.Report).filter(model.Report.id == report_id).first()

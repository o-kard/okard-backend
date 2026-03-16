from sqlalchemy.orm import Session
from uuid import UUID
from . import model, schema
from src.modules.common.enums import ReportStatus
from datetime import datetime, timezone

def create_report(db: Session, reporter_id: UUID, data: schema.ReportCreate) -> model.Report:
    db_obj = model.Report(
        campaign_id=data.campaign_id,
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

def get_reports(db: Session) -> list[model.Report]:
    return db.query(model.Report).order_by(model.Report.created_at.desc()).all()

def update_report_status(db: Session, report_id: UUID, status: ReportStatus) -> model.Report:
    report = get_report(db, report_id)
    if report:
        report.status = status
        if status == ReportStatus.reviewed:
            report.resolved_at = datetime.now(timezone.utc)
        else:
            report.resolved_at = None
        db.commit()
        db.refresh(report)
    return report

def delete_report(db: Session, report_id: UUID) -> bool:
    report = get_report(db, report_id)
    if report:
        db.delete(report)
        db.commit()
        return True
    return False

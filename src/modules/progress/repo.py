from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_progress(db: Session, post_id: UUID | None = None):
    query = db.query(model.Progress)
    if post_id:
        query = query.filter(model.Progress.post_id == post_id)
    return query.all()

def get_progress(db: Session, progress_id: UUID):
    return db.query(model.Progress).filter(model.Progress.id == progress_id).first()

def create_progress(db: Session, progress: schema.ProgressCreate):
    db_progress = model.Progress(**progress.model_dump())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def update_progress(db: Session, db_progress: model.Progress, data: schema.ProgressUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_progress, key, value)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def delete_progress(db: Session, db_progress: model.Progress):
    db.delete(db_progress)
    db.commit()
    return db_progress

from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_media(db: Session):
    return db.query(model.Media).all()

def get_media(db: Session, media_id: UUID):
    return db.query(model.Media).filter(model.Media.id == media_id).first()

def create_media(db: Session, media: model.Media):
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

def delete_media(db: Session, db_media: model.Media):
    db.query(model.MediaHandler).filter(model.MediaHandler.media_id == db_media.id).delete()
    db.delete(db_media)
    db.commit()
    return db_media

from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_images(db: Session):
    return db.query(model.Image).all()

def get_image(db: Session, image_id: UUID):
    return db.query(model.Image).filter(model.Image.id == image_id).first()

def create_image(db: Session, image: model.Image):
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def delete_image(db: Session, db_image: model.Image):
    db.query(model.ImageHandler).filter(model.ImageHandler.image_id == db_image.id).delete()
    db.delete(db_image)
    db.commit()
    return db_image

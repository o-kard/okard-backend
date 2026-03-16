from sqlalchemy.orm import Session
from . import model, schema
from uuid import UUID

def list_informations(db: Session):
    return db.query(model.Information).all()

def get_information(db: Session, information_id: UUID):
    return db.query(model.Information).filter(model.Information.id == information_id).first()

def create_information(db: Session, information: schema.InformationCreate):
    db_information = model.Information(**information.model_dump())
    db.add(db_information)
    db.commit()
    db.refresh(db_information)
    return db_information

def update_information(db: Session, db_information: model.Information, data: schema.InformationUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_information, key, value)
    db.commit()
    db.refresh(db_information)
    return db_information

def delete_information(db: Session, db_information: model.Information):
    db.delete(db_information)
    db.commit()
    return db_information

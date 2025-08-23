# modules/country/repo.py
from uuid import UUID
from sqlalchemy.orm import Session
from . import model, schema

def get_country_by_id(db: Session, country_id: UUID):
    return db.query(model.Country).filter(model.Country.id == country_id).first()

def get_countries(db: Session):
    return db.query(model.Country).where(model.Country.enabled == True).all()